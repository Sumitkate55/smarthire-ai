"""
Collection gateway for resumes and scores.

Uses MongoDB when a working MONGODB_URI is configured. Otherwise it falls back
to Django ORM models, which gives the project persistent local/deployable
storage without requiring MongoDB Atlas.
"""
from __future__ import annotations

import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

_client = None
_db = None
_mongo_available = None   # None = not tested yet


def _get_db():
    global _client, _db, _mongo_available
    if _mongo_available is False:
        return None
    if getattr(settings, 'TESTING', False):
        _mongo_available = False
        return None
    if _db is not None:
        return _db
    uri = getattr(settings, 'MONGODB_URI', '')
    if not uri:
        logger.warning("MONGODB_URI not set — running without MongoDB.")
        _mongo_available = False
        return None
    try:
        from pymongo import MongoClient
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _client.admin.command('ping')          # test connection
        _db = _client['smarthire']
        _mongo_available = True
        logger.info("MongoDB connected.")
        return _db
    except Exception as exc:
        logger.error(f"MongoDB connection failed: {exc}")
        _mongo_available = False
        return None


def _parse_datetime(value):
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError:
            return timezone.now()
    else:
        return timezone.now()

    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _apply_projection(doc, projection):
    if not projection:
        return dict(doc)

    include_keys = {key for key, enabled in projection.items() if enabled}
    exclude_keys = {key for key, enabled in projection.items() if not enabled}

    if include_keys:
        projected = {key: value for key, value in doc.items() if key in include_keys}
        if projection.get('_id', 1) != 0 and '_id' in doc:
            projected['_id'] = doc['_id']
        return projected

    projected = dict(doc)
    for key in exclude_keys:
        projected.pop(key, None)
    return projected


class _MemCollection:
    """
    In-memory fallback collection that mimics the pymongo Collection API
    used in this project (insert_one, find, find_one, count_documents).
    Data is stored per-process and is lost on restart — acceptable as a
    local-dev / no-MongoDB fallback.
    """
    _store = {}   # class-level so all instances of same name share data

    def __init__(self, name):
        self.name = name
        if name not in _MemCollection._store:
            _MemCollection._store[name] = []

    @property
    def _docs(self):
        return _MemCollection._store[self.name]

    def insert_one(self, doc):
        self._docs.append(dict(doc))
        return type('R', (), {'inserted_id': id(doc)})()

    def find(self, query=None, projection=None, sort=None, limit=None):
        results = [d for d in self._docs if self._match(d, query or {})]
        if sort:
            for key, direction in reversed(sort):
                results.sort(key=lambda d: d.get(key, ''), reverse=(direction == -1))
        if limit:
            results = results[:limit]
        return _Cursor([_apply_projection(doc, projection) for doc in results])

    def find_one(self, query=None, projection=None):
        results = list(self.find(query, projection))
        return results[0] if results else None

    def count_documents(self, query=None):
        return len([d for d in self._docs if self._match(d, query or {})])

    def _match(self, doc, query):
        for k, v in query.items():
            if doc.get(k) != v:
                return False
        return True


class _Cursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, key, direction=-1):
        self._docs.sort(key=lambda d: d.get(key, ''), reverse=(direction == -1))
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


class _OrmCollection:
    def __init__(self, name):
        self.name = name

    def _model(self):
        if self.name == 'resumes':
            from apps.resumes.models import ResumeRecord

            return ResumeRecord
        if self.name == 'scores':
            from apps.scoring.models import ScoreRecord

            return ScoreRecord
        return None

    def _to_document(self, instance):
        return instance.to_document()

    def insert_one(self, doc):
        model = self._model()
        if model is None:
            return _MemCollection(self.name).insert_one(doc)

        payload = dict(doc)
        payload.pop('_id', None)

        if self.name == 'resumes':
            instance = model.objects.create(
                resume_id=payload.get('resume_id'),
                user_id=payload['user_id'],
                username=payload.get('username', ''),
                label=payload.get('label', ''),
                filename=payload.get('filename', ''),
                raw_text=payload.get('raw_text', ''),
                extracted_skills=payload.get('extracted_skills', []),
                uploaded_at=_parse_datetime(payload.get('uploaded_at')),
            )
        else:
            instance = model.objects.create(
                score_id=payload.get('score_id'),
                user_id=payload['user_id'],
                resume_id=str(payload.get('resume_id', '')),
                best_role=payload.get('best_role', ''),
                match_percentage=payload.get('match_percentage', 0),
                matched_skills=payload.get('matched_skills', []),
                missing_skills=payload.get('missing_skills', []),
                top_roles=payload.get('top_roles', []),
                ai_suggestion=payload.get('ai_suggestion', ''),
                resume_score=payload.get('resume_score', 0),
                scored_at=_parse_datetime(payload.get('scored_at')),
            )

        return type('R', (), {'inserted_id': instance.pk})()

    def find(self, query=None, projection=None, sort=None, limit=None):
        model = self._model()
        if model is None:
            return _MemCollection(self.name).find(query, projection, sort, limit)

        queryset = model.objects.filter(**(query or {}))
        docs = [_apply_projection(self._to_document(instance), projection) for instance in queryset]
        cursor = _Cursor(docs)
        if sort:
            for key, direction in reversed(sort):
                cursor.sort(key, direction)
        if limit:
            cursor.limit(limit)
        return cursor

    def find_one(self, query=None, projection=None):
        results = list(self.find(query=query, projection=projection, limit=1))
        return results[0] if results else None

    def count_documents(self, query=None):
        model = self._model()
        if model is None:
            return _MemCollection(self.name).count_documents(query)
        return model.objects.filter(**(query or {})).count()


def _get_collection(name):
    db = _get_db()
    if db is not None:
        return db[name]
    if name in {'resumes', 'scores'}:
        return _OrmCollection(name)
    return _MemCollection(name)


# Public accessors
def resumes_col():  return _get_collection('resumes')
def scores_col():   return _get_collection('scores')
def jobs_col():     return _get_collection('jobs')

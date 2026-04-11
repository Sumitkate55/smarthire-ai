"""
MongoDB connection manager.
Safe: if MONGODB_URI is missing/invalid, all collection methods return a
lightweight in-memory stub so the rest of the app still boots.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None
_db = None
_mongo_available = None   # None = not tested yet


def _get_db():
    global _client, _db, _mongo_available
    if _mongo_available is False:
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
        # Apply projection (exclude _id etc.)
        if projection:
            filtered = []
            for doc in results:
                filtered.append({k: v for k, v in doc.items()
                                 if projection.get(k, 1) != 0})
            return _Cursor(filtered)
        return _Cursor(results)

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


def _get_collection(name):
    db = _get_db()
    if db is not None:
        return db[name]
    return _MemCollection(name)


# Public accessors
def resumes_col():  return _get_collection('resumes')
def scores_col():   return _get_collection('scores')
def jobs_col():     return _get_collection('jobs')

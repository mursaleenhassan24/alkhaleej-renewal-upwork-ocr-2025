from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime


class MongoDB:
    def __init__(self, connection_string: str, database_name: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]
    
    async def close(self):
        self.client.close()


class CRUDOperations:
    def __init__(self, mongodb: MongoDB, collection_name: str):
        self.collection = mongodb.get_collection(collection_name)
    
    # CREATE
    async def create(self, data: Dict[str, Any]) -> str:
        """Insert a document and return its ID"""
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)
    
    # READ - Get by ID
    async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID"""
        document = await self.collection.find_one({"_id": ObjectId(doc_id)})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    # READ - Get all
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all documents with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return documents
    
    # READ - Find by filter
    async def find(self, filter_query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find documents matching a filter"""
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return documents
    
    # READ - Find one by filter
    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching a filter"""
        document = await self.collection.find_one(filter_query)
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    # UPDATE
    async def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document by ID"""
        data["updated_at"] = datetime.utcnow().isoformat()
        result = await self.collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    # UPDATE - Update by filter
    async def update_many(self, filter_query: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Update multiple documents matching a filter"""
        data["updated_at"] = datetime.utcnow().isoformat()
        result = await self.collection.update_many(
            filter_query,
            {"$set": data}
        )
        return result.modified_count
    
    # DELETE
    async def delete(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
    
    # DELETE - Delete by filter
    async def delete_many(self, filter_query: Dict[str, Any]) -> int:
        """Delete multiple documents matching a filter"""
        result = await self.collection.delete_many(filter_query)
        return result.deleted_count
    
    # COUNT
    async def count(self, filter_query: Dict[str, Any] = None) -> int:
        """Count documents matching a filter"""
        if filter_query is None:
            filter_query = {}
        return await self.collection.count_documents(filter_query)
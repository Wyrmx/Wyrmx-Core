from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from abc import ABC
from typing import Type, TypeVar, List

T = TypeVar("T", bound="Model")


class Model(ABC):

    __schema__ = DeclarativeBase
    __Session__: sessionmaker[Session] = None


    @classmethod
    def bindSession(cls: Type[T], session: sessionmaker[Session]): cls.__Session__ = session


    def __filterAutoIncrement(self, data: dict):


        autoIncColumns = {
            col.name
            for col in self.__schema__.__table__.columns
            if col.autoincrement == True
        }


        return {key: value for key, value in data.items() if key not in autoIncColumns}
    


    def __filterInternalAttributes(self):

        
        classPrefix = f"_{self.__class__.__name__}__"

        return {
            (key.split(classPrefix, 1)[1] if key.startswith(classPrefix) else key): value
            for key, value in self.__dict__.items()
            if key not in ["__schema__", "__Session__"]
        }
        
        
        


    
    def create(self):

        """
        Insert this model instance as a new row in the database.
        Commits the transaction automatically.
        """


        if not self.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        
        with self.__Session__() as session: 

            try: 
                schemaInstance = self.__schema__(**self.__filterAutoIncrement(self.__filterInternalAttributes()))
                session.add(schemaInstance)
                session.commit()

            finally: session.close()
    
    
    


    def save(self):

        """
        Save this model instance.
        If it already exists (primary key present), update the record.
        Otherwise, insert as new.
        """

        if not self.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        
        with self.__Session__() as session: 

            try: 
                schemaInstance = self.__schema__(**self.__filterAutoIncrement(self.__filterInternalAttributes()))
                session.merge(schemaInstance)
                session.commit()

            finally: session.close()

        
    
    
    def delete(self):

        """
        Delete this model instance from the database.
        Commits the transaction automatically.
        """

        if not self.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        
        with self.__Session__() as session: 

            try: 
                schemaInstance = session.query(self.__schema__).filter_by(**self.__filterInternalAttributes()).first()
                session.delete(schemaInstance)
                session.commit()

            finally: session.close()



    
    @classmethod
    def get(cls: Type[T], **filters) -> T: 

        """
        Class method.
        Retrieve a single record matching given filters.
        Example: UserModel.get(id=1)
        Returns a model instance or None.
        """

        if not cls.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        with cls.__Session__() as session: 

            schemaRecord = session.query(cls.__schema__).filter_by(**filters).first()
            
            return cls(**{
                column.name: getattr(schemaRecord, column.name) for column in cls.__schema__.__table__.columns
            })




    @classmethod
    def filter(cls: Type[T], **filters) -> List[T]:

        """
        Class method.
        Retrieve multiple records matching given filters.
        Example: UserModel.filter(is_active=True)
        Returns a list of model instances.
        """


        if not cls.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        with cls.__Session__() as session: 

            schemaRecords = session.query(cls.__schema__).filter_by(**filters).all()
            
        
            return [
                cls(**{
                    column.name: getattr(schemaRecord, column.name) for column in cls.__schema__.__table__.columns
                })

                for schemaRecord in schemaRecords
            ]



    @classmethod
    def all(cls: Type[T]) -> List[T]: 

        """
        Class method.
        Retrieve all rows in this model’s table.
        Returns a list of model instances.
        """

        if not cls.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        with cls.__Session__() as session: 

            schemaRecords = session.query(cls.__schema__).all()
            
        
            return [
                cls(**{
                    column.name: getattr(schemaRecord, column.name) for column in cls.__schema__.__table__.columns
                })

                for schemaRecord in schemaRecords
            ]


    

    @classmethod
    def count(cls: Type[T], **filters) -> List[T]:

        """
        Class method.
        Count rows matching given filters.
        If no filters, counts all rows.
        """

        if not cls.__Session__: raise RuntimeError("Session not bound. Call Model.bindSession first.")
        with cls.__Session__() as session: return session.query(cls.__schema__).filter_by(**filters).count()


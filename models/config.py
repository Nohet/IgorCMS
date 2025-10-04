from pydantic import BaseModel, PositiveInt, SecretStr


class MySQLServerModel(BaseModel):
    user: str
    password: str
    host: str
    port: PositiveInt
    database_name: str


class ConfigModel(BaseModel):
    database: MySQLServerModel
    secret_key: SecretStr

from typing import Union
from pydantic import BaseModel

class SPDRequest(BaseModel):
    protectedAttribute: str
    favorableOutcome: Union[int, float, str]
    outcomeName: str
    privilegedValue: Union[int, float, str]
    unprivilegedValue: Union[int, float, str]

class DIRRequest(BaseModel):
    protectedAttribute: str
    favorableOutcome: Union[int, float, str]
    outcomeName: str
    privilegedValue: Union[int, float, str]
    unprivilegedValue: Union[int, float, str]


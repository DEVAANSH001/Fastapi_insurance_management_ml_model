from pydantic import BaseModel , EmailStr , AnyUrl , Field
from typing import List , Dict , Optional , Annotated

class patients(BaseModel):
    name : Annotated[str , Field(min_length=1, max_length=50, description="Name must be between 1 and 50 characters")]
    age : int
    linkdin : AnyUrl
    emial : EmailStr
    weight : float = Field(gt=0, description="Weight must be greater than 0")
    allergies : Optional[List[str]] = None
    contants : Dict[str, str]
    
    
def insert_patient(patient: patients):
    
    print(patient.name)
    print(patient.age)
    print ("start")

patients_info = {'name': 'John Doe', 'age': 30 , 'weight': 70.5,'allergies': ['pollen', 'nuts'], 'contants': {'phone': '123-456-7890'}}

patient = patients(**patients_info)

insert_patient(patient)
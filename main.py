from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, computed_field
from fastapi.responses import JSONResponse

from typing import List, Dict, Optional, Annotated , Literal
import json

app = FastAPI()

class Patients(BaseModel):
    id : Annotated[str , Field(...,description="id of a patients " , examples=["P001"])]
    name: Annotated[str , Field(..., min_length=1, max_length=50, description="Name must be between 1 and 50 characters")]
    age: Annotated[int , Field(..., ge=0, description="Age must be a non-negative integer")]
    city : Annotated[str , Field(..., min_length=1, max_length=100, description="City must be between 1 and 100 characters")]
    height: Annotated[float , Field(..., gt=0, description="Height must be greater than 0")]
    weight: Annotated[float , Field(..., gt=0, description="Weight must be greater than 0")]
    
    @computed_field
    @property
    def bmi(self) -> float:
          bmi = round(self.weight / (self.height ** 2), 2)
          return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if (self.bmi < 18.5):
            return "Under weight"
        elif (self.bmi < 25):
            return "Normal weight"
        elif (self.bmi >= 25):
            return "Obese"
        

class PatientUpdate(BaseModel):
    Iname: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data

def save_data(data):
    with open('patients.json', 'w') as file:
        json.dump(data , file)

@app.get('/')
def hello():
    return {'message': 'patients data '}


@app.get('/intro')
def intro():
    return {'message': 'ez win'}

#end point to get all patients
@app.get('/patients')
def view():
    data = load_data()
    return data

@app.get('/view/{patient_id}')
def view_patient(patient_id: str = Path(..., description="The ID of the patient to view" , example="P001")):
    data = load_data()
    
    if(patient_id in data):
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query( ... , description='Sort on the basis of height, weightor bmi'), order: str = Query('asc', description='sort in asc or desc order') ):
    valid_feilds = ['height', 'weight', 'bmi']  
    if sort_by not in valid_feilds:
        raise HTTPException(status_code=400, detail="Invalid sort field. Choose from height, weight, or bmi.")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Choose either 'asc' or 'desc'.")
    data = load_data()
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    
    return sorted_data

@app.post('/create')
def createpatient(patient : Patients):
    # load the dataset 
    data = load_data()
    #check for duplicate
    if patient.id in data:
        return HTTPException(status_code=400 , detail="data already exists ")
    #add if new 
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    #save into json 
    save_data(data)
    
    return JSONResponse(status_code=201 , content={'message' : "patient created sucessfully"})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patients(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})

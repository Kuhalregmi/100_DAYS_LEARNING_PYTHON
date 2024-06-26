import os
from dotenv import load_dotenv
from data_manager import DataManager
from pprint import pprint
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager

load_dotenv()

#GLOBAL VARIABLE SECTION 
DEPARATURE_LOCATION=input("Enter The Departure Loacation:").title()
DEPRATURE_LOCATION_IATA_CODE= None
account_sid = os.getenv('TWILIO_SSID')
auth_token = os.getenv('TWILIO_AUTH')
 
RECEIPIENT_NUMBER=['+97724273574','+9779840305547','+918217570031']

datamanager= DataManager()#datamanger class object
flightsearch= FlightSearch()#flight manager class object
flightdata = FlightData()#flight data class object
notifiactionmanager = NotificationManager(ssid=account_sid, auth_token=auth_token)#twillo class object

DEPRATURE_LOCATION_IATA_CODE =flightsearch.iata_code(DEPARATURE_LOCATION)

#TODO CHECKING IF DEPRATURE_LOCATION_IATA_CODE IS AVALIABLE IN THE API OR NOT 
if DEPRATURE_LOCATION_IATA_CODE == None:
    print("\nSorry! IATA code is NOT avaliable in the API :( \nHINTS: Enter the IATA CODE manually from google..")
    DEPRATURE_LOCATION_IATA_CODE= input(f"\nEnter the IATA code of {DEPARATURE_LOCATION} city: ").upper()


sheet_data = datamanager.get_data()
a =-1
# using flight_data to insert iataCode to the sheet
for data in sheet_data:
    if data['iataCode']=="":
        a = sheet_data.index(data)
        data['iataCode']=flightsearch.iata_code(cityname=data['city'])
                   
#updating the iataCode to the Google Sheet 
if a>=0:
    datamanager.destination_data = sheet_data
    datamanager.update_destination_codes()
    
#checking the flights avaliable     
for data in sheet_data:
    result = flightsearch.fetch_flight_data(departure=DEPRATURE_LOCATION_IATA_CODE,destination=data['iataCode'])
    cheapest_flight=flightdata.find_cheapest_flight(flight_data=result) 
    
    
    try:
        message_body = (f"Low price alert! \nOnly £{cheapest_flight.price} to fly"
                        f" with {cheapest_flight.airline_name} from {DEPARATURE_LOCATION.upper()} ({cheapest_flight.departure_airport_code})"
                        f" to {data['city'].upper()} ({cheapest_flight.destination_airport_code}), "
                        f"on {cheapest_flight.departure_date.split('T')[0]} until {cheapest_flight.return_date.split('T')[0]}.")
        
        
        if cheapest_flight.price != "N/A" and float(cheapest_flight.price)<= float(data['lowestPrice']):
            for item in RECEIPIENT_NUMBER:
                notifiactionmanager.send_whatsapp_message(message=message_body, recipient= item)
            
    except AttributeError as e:
        pass 
        


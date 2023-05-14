# main.py
# Author: Simon Wollerton, simon@penguinpowered.co.uk
""" A utility application written in Python and Tkinter to calculate monthly mileage expenses. """

import os
import sys
import subprocess
import csv
import requests
import time
import smtplib
import ssl
import zipfile
import threading
import openpyxl

from pathlib import Path
from openpyxl import Workbook
from configparser import ConfigParser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

name = ""
month_ending = ""
vehicle_make_reg = ""
initial_start_miles = ""
initials = ""
mail_server = ""
mail_server_port = ""
login_email = ""
password = ""
email_subject = ""
sender_email = ""
sender_name = ""
receiver_email = ""
receiver_name = ""
cc_email = ""
bcc_email = ""
email_message = ""
data_path = ""
output_path = ""
email_included = ""
backup_included = ""
openRouteService_api_key = ""
input_data = ""
write_csv_output = ""
send_file = ""
subject = ""
body = ""

app = Path(__file__).parent
settings_folder = app / Path("./settings")
input_folder = app / Path("./input")
output_folder = app / Path("./output")
assets_folder = app / Path("./assets")


def settingsfolder(path: str) -> Path:
    return settings_folder / Path(path)


def inputfolder(path: str) -> Path:
    return input_folder / Path(path)


def outputfolder(path: str) -> Path:
    return output_folder / Path(path)


def assetsfolder(path: str) -> Path:
    return assets_folder / Path(path)


# Initial app status
app_status_update = ""


# Load the config data
def load_config_data():
    global name
    global month_ending
    global vehicle_make_reg
    global initial_start_miles
    global initials
    global mail_server
    global mail_server_port
    global login_email
    global password
    global email_subject
    global sender_email
    global sender_name
    global receiver_email
    global receiver_name
    global cc_email
    global bcc_email
    global email_message
    global data_path
    global output_path
    global email_included
    global backup_included
    global openRouteService_api_key
    global input_data
    global write_csv_output
    global send_file
    global subject
    global body

    # Read default.ini file for config
    config = ConfigParser()
    config.read("./settings/default.ini")

    # User data
    name = config.get("Driver", "name")
    month_ending = config.get("Driver", "month_ending")
    vehicle_make_reg = config.get("Driver", "vehicle_make_reg")
    initial_start_miles = config.getint("Driver", "initial_start_miles")
    initials = config.get("Driver", "initials")

    # Mail Server data
    mail_server = config.get("MailServer", "mail_server")
    mail_server_port = config.getint("MailServer", "mail_server_port")
    login_email = config.get("MailServer", "login_email")
    password = config.get("MailServer", "password")

    # Email content data
    email_subject = config.get("MailContent", "email_subject")
    sender_email = config.get("MailContent", "sender_email")
    sender_name = config.get("MailContent", "sender_name")
    receiver_email = config.get("MailContent", "receiver_email")
    receiver_name = config.get("MailContent", "receiver_name")
    cc_email = config.get("MailContent", "cc_email")
    bcc_email = config.get("MailContent", "bcc_email")
    email_message = config.get("MailContent", "email_message")

    # Backup data
    data_path = config.get("Backup", "data_path")
    output_path = config.get("Backup", "output_path")

    # Run config
    email_included = config.get("Run", "email")
    backup_included = config.get("Run", "backup")

    # API keys
    openRouteService_api_key = config.get("ApiKey", "openRouteService_api_key")

    # File input and output data.
    input_data = csv.reader(open("./input/data.csv", "r"))
    write_csv_output = open("./output/" + month_ending + ".csv", "w")

    # File attachment file name
    send_file = "./output/" + month_ending + ".csv"

    # Email subject
    subject = email_subject

    # Email main body
    body = (
        "Hello "
        + receiver_name
        + "\n\n"
        + email_message
        + " "
        + month_ending
        + ".\n\nThank you\n\n"
        + sender_name
    )


# Calculate mileage returns from input data
def mileage_returns():
    global app_status_update
    global initial_start_miles
    _start_miles = initial_start_miles
    private_miles = 0
    end_miles = 0
    total_business_miles = 0
    total_private_miles = 0

    app_status_update = "Running please wait..."

    write_csv_output.write(
        "Name: " + name + "\n" + "Month Ending: " + month_ending + "\n"
        "Vehicle Make \\ Model & Registration: " + vehicle_make_reg + "\n\n"
    )

    write_csv_output.write(
        "Date,"
        + "Destination,"
        + "Start Mileage,"
        + "End Mileage,"
        + "Business Miles,"
        + "Private Miles,"
        + "Balance,"
        + "Initials"
        + "\n"
    )

    for row in input_data:
        time.sleep(2)
        destination_date = row[0]
        start_location = row[1]
        end_location = row[3]
        start_postcode = row[2]
        end_postcode = row[4]
        purpose = row[5]

        first_postcode = requests.get(
            "https://api.postcodes.io/postcodes/" + start_postcode
        )
        second_postcode = requests.get(
            "https://api.postcodes.io/postcodes/" + end_postcode
        )

        first_postcode_data = first_postcode.json()
        second_postcode_data = second_postcode.json()

        start_long = first_postcode_data["result"]["longitude"]
        start_lat = first_postcode_data["result"]["latitude"]

        end_long = second_postcode_data["result"]["longitude"]
        end_lat = second_postcode_data["result"]["latitude"]
        start = str(start_long) + "," + str(start_lat)
        end = str(end_long) + "," + str(end_lat)

        get_distance = requests.get(
            "https://api.openrouteservice.org/v2/directions/driving-car?api_key="
            + openRouteService_api_key
            + "&start="
            + start
            + "&end="
            + end
        )
        distance_data = get_distance.json()
        distance = distance_data["features"][0]["properties"]["segments"][0]["distance"]
        miles = distance / 1609.344
        business_miles = round(miles)
        start_miles = _start_miles
        _start_miles += business_miles
        end_miles = _start_miles

        if purpose >= "private":
            business_miles = 0
            private_miles = round(miles)

        elif purpose >= "business":
            private_miles = 0

        balance_miles = private_miles + business_miles
        total_business_miles += business_miles
        total_private_miles += private_miles

        total_miles = total_business_miles + total_private_miles

        write_csv_output.write(
            str(destination_date)
            + ","
            + start_location
            + " "
            + start_postcode
            + " to "
            + end_location
            + " "
            + end_postcode
            + ","
            + str(start_miles)
            + ","
            + str(end_miles)
            + ","
            + str(business_miles)
            + ","
            + str(private_miles)
            + ","
            + str(balance_miles)
            + ","
            + initials
            + "\n"
        )

    write_csv_output.write(
        "\n"
        + "Total Business Miles: "
        + str(total_business_miles)
        + " , "
        + "Total Private Miles: "
        + str(total_private_miles)
        + " , "
        + "Total miles: "
        + str(total_miles)
        + " , "
        + "Vehicle Odometer: "
        + " "
        + str(end_miles)
    )

    write_csv_output.close()

    app_status_update = "Mileage Expenses completed."


# Convert output csv file to Excel spreadsheet and add signature
def convert_csv_to_excel():
    global app_status_update
    wb = Workbook()
    ws = wb.active

    with open("./output/" + month_ending + ".csv") as f:
        for row in csv.reader(f):
            ws.append(row)

    img = openpyxl.drawing.image.Image("./assets/signature.png")
    last_row = len(list(ws.rows))
    img_row = str(last_row + 1)
    img.anchor = "B" + img_row
    ws.add_image(img)
    wb.save("./output/" + month_ending + ".xlsx")

    app_status_update = "Excel spreadsheet completed."


# Email mileage return csv to configured email recipients from the settings data
def email_mileage_returns():
    global app_status_update
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Cc"] = cc_email
    message["Bcc"] = bcc_email

    message.attach(MIMEText(body, "plain"))

    with open(send_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {send_file}",
    )

    message.attach(part)
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(mail_server, mail_server_port, context=context) as server:
        server.login(login_email, password)
        server.sendmail(sender_email, [receiver_email, cc_email, bcc_email], text)

        app_status_update = "Mileage expenses sent by email."


# Backup the output directory to separate backup folder
def backup():
    global app_status_update
    with zipfile.ZipFile(data_path + month_ending + ".zip", mode="w") as zipf:
        len_dir_path = len(data_path)
        for root, _, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])

            app_status_update = "Backup completed."


# Run main application conditions
def run_main():
    global app_status_update

    load_config_data()

    if email_included >= "yes" and backup_included >= "no":
        mileage_returns()
        convert_csv_to_excel()
        email_mileage_returns()

        app_status_update = "All completed OK. Thank you"

    elif email_included >= "no" and backup_included >= "yes":
        mileage_returns()
        convert_csv_to_excel()
        backup()

        app_status_update = "All completed OK. Thank you"

    elif email_included >= "yes" and backup_included >= "yes":
        mileage_returns()
        convert_csv_to_excel()
        email_mileage_returns()
        backup()

        app_status_update = "All completed OK. Thank you"

    elif email_included >= "no" and backup_included >= "no":
        mileage_returns()
        convert_csv_to_excel()

        app_status_update = "All completed OK. Thank you"


# Run main in a thread
def run_main_thread():
    threading.Thread(target=run_main).start()


# Edit settings function
def edit_settings():
    if sys.platform >= "win32":
        os.startfile(".\\settings\\default.ini", "open")
    else:
        opener = "open" if sys.platform >= "darwin" else "xdg-open"
        subprocess.call([opener, "./settings/default.ini"])


# Edit data function
def edit_data():
    if sys.platform >= "win32":
        os.startfile(".\\input\\data.csv", "open")
    else:
        opener = "open" if sys.platform >= "darwin" else "xdg-open"
        subprocess.call([opener, "./input/data.csv"])

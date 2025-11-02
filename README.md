# SVAIS

Maritime transport is essential to the global economy but faces major challenges due to fraudulent activities, such as the falsification of vessel positioning data. Although the AIS (Automatic Identification System) technology is critical for monitoring and managing maritime traffic, its reliability is not always guaranteed, posing risks to safety and the efficient management of resources.

This project proposes AIS data validation and verification techniques through an interactive and customizable web interface. This visual and effective tool assists maritime control authorities in detecting and preventing anomalous activities, strengthening the security, integrity, efficiency, and transparency of global maritime transport management.

![Screenshot 2024-07-23 112853](https://github.com/user-attachments/assets/cfaba239-1e37-4cef-8763-3dcd5c6ac478)

## Web Server

The project provides an interactive web interface adaptable to any device for monitoring and filtering information about detected vessels and verifying their positions. This is achieved through a radiogoniometry system that provides signal incidence angles, used in a triangulation algorithm to calculate a 95% confidence ellipse, identifying fraudulent positions and notifying the user.

The web application offers two operating modes: **Surveillance**, for real-time monitoring, and **Simulation**, to train operators with predefined scenarios. It also allows querying each vessel’s history to detect anomalous routes and alert the user. Additionally, pre-recorded AIS messages can be decoded and visualized.

Access to features is managed through three user roles:
- **Base:** access to Surveillance mode only.  
- **Operators:** full access.  
- **Administrators:** full access and database management capabilities.  

To protect sensitive data, a **facial recognition system** was implemented as a two-step verification method.

![Screenshot 2024-07-23 113103](https://github.com/user-attachments/assets/6f370a3d-7080-4202-bf78-8b2755dafef0)

![Screenshot 2024-07-23 113131](https://github.com/user-attachments/assets/84ef45c2-2e17-4aea-8ebb-870adc8163bf)

## AIS Receiver and Decoder

The system includes a receiver node located on the coast, consisting of a **Raspberry Pi** connected to a **software-defined radio (SDR)**. This setup captures AIS radio signals, decodes them, and transmits the data to the web server through an LTE connection.

The decoder implementation was carried out in two phases:  
1. A MATLAB prototype was developed and tested with pre-recorded AIS signals.  
2. The algorithm was reimplemented in Python, comparing outputs from both systems to ensure consistent and correct operation.

![Screenshot 2024-07-23 113455](https://github.com/user-attachments/assets/3c21f029-2b84-4c31-94ca-cd23779ec325)

An AIS system transmits vessel data via a **VHF transmitter**, using channels **87B** and **88B** (frequencies 161.975 MHz and 162.025 MHz) with **GMSK modulation at 9.6 kbit/s** over 25 kHz channels, following the **HDLC protocol**. The message structure and types comply with **ITU-R M.1371-5 (02/2014)** recommendations.

![Screenshot 2024-07-23 113542](https://github.com/user-attachments/assets/6c795e29-1dd6-4f24-b980-dae1ca5aa9ec)

## Photovoltaic Power System

![Screenshot 2024-07-23 114000](https://github.com/user-attachments/assets/5234c594-bf43-47fe-8456-42bff88d7c4c)

The power system consists of four main components:

- **Solar Panel:** Captures available solar energy and converts it into electricity.  
- **Charge Controller:** Regulates the energy flow to the Raspberry Pi or a rechargeable battery, ensuring optimal and safe charging without compromising autonomy.  
- **Rechargeable Battery:** Stores energy for later use when direct power is unavailable.  
- **Step-Down Converter:** Adjusts the controller’s output voltage to suitable levels for the Raspberry Pi’s power requirements.

![1000022877](https://github.com/user-attachments/assets/586d95e0-c5e9-4451-b95f-b4001f84520b)

## Technologies

![Screenshot 2024-07-23 114113](https://github.com/user-attachments/assets/6096bb5f-ea02-41ca-a8c7-a6a3b40ecb73)

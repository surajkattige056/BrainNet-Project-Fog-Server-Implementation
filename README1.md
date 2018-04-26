# BrainNet-Project-Fog-Server-Implementation
This is an implementation of the Fog and Cloud servers in the BrainNet project

Description:
-------------
The client program acts like an android app sending a .edf file having brain signals of the user. The server file receives this file
and parses through the file using the edf_parser function. This function outputs the brain signal values of the user.These signals 
are then compared with the values stored in the database. Note that Support Vector Machine (SVM) machine learning algorithm is used
to train the server using the data from the database. When an incoming signal appears, the signal is parsed and then given as input
to the SVM as test set. This will authenticate whether the incoming brainwave signal belongs to the user or not. This program is used
to authenticate a user.

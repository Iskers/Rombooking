# Rombooking

As of now you have to create a venv in the location in the top folder or add the requirements to your python instance.

Currently you also have to customize your room by inspecting your post packages. This is a bit tricky, but should work with both Chome and Firefox. Open up the Web developer tools from the hamburger menu in the top right of your browser (The F12 key also does the job). Under the network-tab, check the preserve logs button. On Chome, right click the top bar of the listing so you can add and sort for POST requests. <img width="1438" alt="Skjermbilde 2021-09-08 kl  20 41 34" src="https://user-images.githubusercontent.com/22838996/132566632-06e3e6d9-c421-4ed7-bc77-c1450e6e2450.png">

Do one booking, while checking that your post requests are getting added to the logger. The script emulates these logs by posting the same data you would usually add. You most inportantly need to grab the room[] (roomID). It is probably the only thing that needs to be changed under the Room category in the config. You might also want to change your seat. 0 is input for random seat, and if your seat is booked the script will try to book a random seat. 

<img width="1440" alt="Skjermbilde 2021-09-08 kl  20 39 59" src="https://user-images.githubusercontent.com/22838996/132566413-fbc39810-fc3d-4fc3-8a33-df5bae2f6748.png">

The example.config file must lastly be changed to App.config.

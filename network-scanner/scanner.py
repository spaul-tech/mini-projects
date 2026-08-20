import subprocess as sp
n=input("Enter ip : ")
try:
	capture=sp.run(["nmap","-sV",n],capture_output=True,text=True,timeout=30)  #the command
	if capture.returncode==0:
	    with open("report.txt","w") as f:  #overwrites the output in a file
	    	f.write(capture.stdout)
	    print("Scan saved to report.txt")	
	else:
	    print("Scan failed with error: \n",capture.stderr)
except sp.TimeoutExpired:
	 print("Scan timed out after 30 seconds — try a smaller port range or increase timeout.")
except sp.FileNotFoundError:
   print("nmap not found — make sure it's installed and in your PATH.")
	 

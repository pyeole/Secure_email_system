import subprocess
import urllib2,os,csv,urllib
import string, random

#generate session key
def generate_session_key():
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))

def database_lookup(email_ID):
	file_path="local_database/"	
	unity_ID=email_ID.split("@")[0]
	#print unity_ID
	file_path+=unity_ID+".pem"
	flag=0
	if os.path.exists(file_path):
		flag=1
		print "Receiver key found in local database!"
	else:
		print "Looking up web database..."
		read_object=urllib2.urlopen("https://courses.ncsu.edu/csc574/lec/001/CertificateRepo")
		csv_file=csv.reader(read_object)
		for i in csv_file:
			#print i[0]
			if i[0]==unity_ID:
				receiver_certificate=urllib.URLopener()
				receiver_certificate.retrieve(i[1],file_path)
				flag=1
	if flag==0:
		print "Could not find receiver key!"
		exit()
	return

def main():
	print ("Enter the receiver's email: (FORMAT: <unity_id>@ncsu.edu)")
	rcv_id=str(raw_input())
	print ("Enter your message: ")
	msg=str(raw_input())

	database_lookup(rcv_id)
	#sender_key=sender_id + ".pem"
	receiver_key="local_database/"+rcv_id.split("@")[0] + ".pem"
		
#generate session key and write the message to a file
	session_key=generate_session_key()
	#print ("Session key: "+session_key)
	fo1=open('message.txt','w+')
	fo1.write(msg)
	fo1.close()
	fo2=open('session_key.txt','w+')
	fo2.write(session_key)
	fo2.close()

#verify the receiver's public key on root certificate	
	p=subprocess.check_output(["openssl","verify","-CAfile","root-ca.crt",receiver_key])
	print p

#encrypt the message with the session key 
	encrypted_msg = subprocess.check_output(["openssl","enc","-aes-256-cbc","-base64","-A","-in","message.txt","-k",session_key])
	#print ("Encrypted message :" + encrypted_msg)

#encrypt the session key with receiver's public key
	encrypted_session_key = subprocess.check_output(["openssl","rsautl","-encrypt","-inkey",receiver_key,"-certin","-in","session_key.txt"])
	#print ("Encrypted session key :" + encrypted_session_key)

#sign the message
	sign_content=encrypted_session_key+"\n"+"                      "+"\n"+encrypted_msg
	fileobject=open("signed_file.txt","w+")
	fileobject.write(sign_content)
	fileobject.close()

#Hashing the message content
	message_hash_1=subprocess.check_output(["openssl","dgst","-sha1","signed_file.txt"])
    	message_hash=message_hash_1.split(" ")
	fo3=open("hash_content.txt",'w+')
    	fo3.write(message_hash[1])
    	fo3.close()

#Signing the hashed content
	signed_message=subprocess.check_output(["openssl","rsautl","-sign","-inkey","private_key.pem","-in","hash_content.txt"])
	
	message="from: pyeole@ncsu.edu"+",to: "+rcv_id+"\n"+"-----BEGIN CSC574 MESSAGE-----"+"\n"+encrypted_session_key+"\n"+"                      "+"\n"+encrypted_msg+"\n"+"                       "+"\n"+signed_message+"\n"+"-----END CSC574 MESSAGE-----"
	
	print message	
	
	fo3=open("received_mail.txt","w+")
	fo3.write(message)
	fo3.close()

if __name__=="__main__":
	main()

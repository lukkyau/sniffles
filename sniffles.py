from access_points import *
import datetime, sqlite3, time

# Set location and sniff number
location="library"
countNum=5
count=1

# Get approved list of MAC addresses
approved=[]
with open("approvedlist.txt") as file:
    for line in file:
        line = line.strip() #preprocess line
        approved.append(line)

# Create database
conn=sqlite3.connect('signal_strengths.db')
curr=conn.cursor()
curr.execute("CREATE TABLE IF NOT EXISTS signals(collected TEXT, location TEXT)")
curr.execute("CREATE TABLE IF NOT EXISTS lookups(mac TEXT PRIMARY KEY, name TEXT, varNum INTEGER)")

# Scan wifi and write to database
lookupList=curr.execute("SELECT mac, name FROM lookups").fetchall()

def sniffMe():
	# Retrieve wifi information (relies on airport)
	wifi_scanner = get_scanner("en0")
	sniffles=wifi_scanner.get_access_points()
	collectionTime=datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
	
	# Write to database based on whether new/existing access point
	print("SNIFF",count)
	if len(sniffles) > 0:
		curr.execute("INSERT INTO signals(collected,location) VALUES (?,?)",(collectionTime,location))
		print("Time: ",collectionTime)
		print("Location: ",location)
		for i in sniffles:
			print("MAC:", i.bssid," Quality:",i.quality," SSID:",i.ssid )
			if i.bssid in approved:
				if (i.bssid,i.ssid) in lookupList:
					lookupNum=lookupList.index((i.bssid,i.ssid))+1
					curr.execute("UPDATE signals SET APMAC{0}=(?) WHERE collected=(?)".format(lookupNum),(i.bssid,collectionTime,))
					curr.execute("UPDATE signals SET APSTRENGTH{0}=(?) WHERE collected=(?)".format(lookupNum),(i.quality,collectionTime,))
					print("UPDATED - Approved wireless point.")
				else:
					lookupList.append((i.bssid,i.ssid))
					lookupNum=len(lookupList)
					curr.execute("INSERT INTO lookups VALUES (?,?,?)",(i.bssid,i.ssid,lookupNum))
					curr.execute("ALTER TABLE signals ADD COLUMN APMAC{0} TEXT".format(lookupNum))
					curr.execute("ALTER TABLE signals ADD COLUMN APSTRENGTH{0} INTEGER".format(lookupNum))
					curr.execute("UPDATE signals SET APMAC{0}=(?) WHERE collected=(?)".format(lookupNum),(i.bssid,collectionTime,))
					curr.execute("UPDATE signals SET APSTRENGTH{0}=(?) WHERE collected=(?)".format(lookupNum),(i.quality,collectionTime,))
					print("ADDED - Approved wireless point.")
			else:
				print("IGNORED - Not approved wireless point.")

	# Time delay
	time.sleep(5)

# Repeat sniffer
while count < countNum:
	sniffMe()
	count=count+1

# Set nulls to zero for nearest neighbour algorithm
for i in range (1,len(lookupList)+1):
	curr.execute("UPDATE signals SET APSTRENGTH{0}=0 WHERE APSTRENGTH{0} IS NULL".format(i))

conn.commit()
curr.close()
conn.close()
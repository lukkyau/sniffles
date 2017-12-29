from access_points import *
import datetime, sqlite3, time

# Set location
location="room"
countNum=5

# Create database
conn=sqlite3.connect('signal_strengths.db')
curr=conn.cursor()
# curr.execute("DROP TABLE IF EXISTS signals")
# curr.execute("DROP TABLE IF EXISTS lookups")
curr.execute("CREATE TABLE IF NOT EXISTS signals(collected TEXT, location TEXT)")
curr.execute("CREATE TABLE IF NOT EXISTS lookups(mac TEXT PRIMARY KEY, name TEXT, varNum INTEGER)")

# Scan wifi and write to database
lookupList=curr.execute("SELECT mac, name FROM lookups").fetchall()
print(lookupList)

def sniffMe():
	wifi_scanner = get_scanner("en0")
	sniffles=wifi_scanner.get_access_points()
	collectionTime=datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S')
	
	# Write to database based on whether new/existing access point
	print("SNIFF",count)
	if len(sniffles) > 0:
		curr.execute("INSERT INTO signals(collected,location) VALUES (?,?)",(collectionTime,location))
		for i in sniffles:
			print("MAC:", i.bssid," Quality:",i.quality," Time:",collectionTime," Location:",location," SSID:",i.ssid )
			if (i.bssid,i.ssid) in lookupList:
				lookupNum=lookupList.index((i.bssid,i.ssid))+1
				curr.execute("UPDATE signals SET AP{0}=(?) WHERE collected=(?)".format(lookupNum),(i.quality,collectionTime,))
				curr.execute("UPDATE signals SET MAC{0}=(?) WHERE collected=(?)".format(lookupNum),(i.bssid,collectionTime,))
			else:
				print("NEW WIRELESS POINT ADDED")
				lookupList.append((i.bssid,i.ssid))
				lookupNum=len(lookupList)
				curr.execute("INSERT INTO lookups VALUES (?,?,?)",(i.bssid,i.ssid,lookupNum))
				curr.execute("ALTER TABLE signals ADD COLUMN MAC{0} TEXT".format(lookupNum))
				curr.execute("ALTER TABLE signals ADD COLUMN AP{0} INTEGER".format(lookupNum))
				curr.execute("UPDATE signals SET AP{0}=(?) WHERE collected=(?)".format(lookupNum),(i.quality,collectionTime,))
				curr.execute("UPDATE signals SET MAC{0}=(?) WHERE collected=(?)".format(lookupNum),(i.bssid,collectionTime,))

	# Time delay
	time.sleep(5)

# Repeat sniffer
count=0
while count < countNum:
	sniffMe()
	count=count+1

# Set nulls to zero for nearest neighbour algorithm
for i in range (1,len(lookupList)+1):
	curr.execute("UPDATE signals SET AP{0}=0 WHERE AP{0} IS NULL".format(i))

conn.commit()
curr.close()
conn.close()
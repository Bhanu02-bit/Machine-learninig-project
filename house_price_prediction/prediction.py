print("enter marks in subject:")
total=0
for i in range(0,5):
    total=total+int(input(" "))
    
avg=total//5
per=(avg)*100
# sub1,sub2,sub3,sub4,sub5=int(input("enter ur sub marks:"))
if  per>80 :
    print("A grade")
elif per >70 or avg < 80:
    print("B grade") 
elif per >60 or avg<70:
    print("C grade")

else:
    print("D grade")



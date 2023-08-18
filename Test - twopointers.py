ori = 10.0
change1 = True
change2 = True
t1 = [0.0]
v1 = [200.0]
t2 = [0.0, 147.0, 147.5, 163.0, 163.5, 179.0, 179.5, 195.0, 195.5, 196.0, 197.0, 197.25, 197.5, 197.75, 198.25, 198.5,
      198.75, 265.25, 267.25, 281.25, 283.25]
v2 = [100.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 114514.191981, -5.0, -3.0, -2.0, 0.2, 0.5, 0.8, 1.0, 100.0, 1.0,
      100.0, 1.0]

if len(t2) == 0 or t2[0] != 0.0:
    t2.insert(0, 0.0)
    v2.insert(0, 1.0)
cur2 = 0
lim1 = 1
lim2 = 0
if change1:
    lim1 = len(t1)
if change2:
    lim2 = len(t2)
ans = []
for cur1 in range(lim1):
    while cur2 < lim2 and t1[cur1] > t2[cur2]:
        if len(ans) != 0 and t1[cur1-1] == t2[cur2]:
            print("poped", ans[len(ans)-1])
            ans.pop()
        ans.append([t2[cur2], ori/v1[0]*v1[cur1-1]*v2[cur2]])
        cur2 += 1
    ans.append([t1[cur1], ori/v1[0]*v1[cur1]*v2[cur2-1]])
while cur2 < lim2:
    if len(ans) != 0 and t1[lim1-1] == t2[cur2]:
        ans.pop()
    ans.append([t2[cur2], ori/v1[0]*v1[lim1-1]*v2[cur2]])
    cur2 += 1
    
for i in range(len(ans)):
    print(ans[i])

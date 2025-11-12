from User import User
from database_sm import save_user, save_post, cur

u1 = User("Mine", "Sungur")
u2 = User("Tugba", "Sahin")

save_user(u1)
save_user(u2)

p1 = u1.add_post("", "Sleeping is my hobby :3")
p2 = u2.add_post("","Feeling great today :)")
p3 = u2.add_post("","I need a break! >:|")
p4 = u1.add_post("","I have a sweet tooth :P")
p5 = u2.add_post("","Going on a hike right now!")

save_post(p1)
save_post(p2)
save_post(p3)
save_post(p4)
save_post(p5)

rows = cur.execute(
    "SELECT id,image,text FROM post WHERE user_id=? ORDER BY id",
    (u1.id,)
).fetchall()
print("Posts von", u1.first_name, rows)

rows = cur.execute(
    "SELECT id, image,text FROM post ORDER BY id",
).fetchall()
print("Posts von allen", rows)

rows = cur.execute(
    "SELECT id, image,text FROM post ORDER BY createdAt desc LIMIT 1",
).fetchall()
print("Letzer post", rows)




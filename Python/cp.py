def process:
     cap = cv2.VideoCapture(filename)
     ret, frame = cap.read()

      while ret:
          ret, frame = cap.read()
#detection part in my case I use tensorflow then 
     # end of detection part 
          q.put(result_of_detection)

def Display():
  while True:
    if q.empty() != True:
        frame = q.get()
        cv2.imshow("frame1", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if __name__ == '__main__':
#  start threads
p1 = threading.Thread(target=process)
p2 = threading.Thread(target=Display)
p1.start()
p2.start()
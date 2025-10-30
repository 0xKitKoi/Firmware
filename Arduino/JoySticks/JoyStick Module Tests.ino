// JoyStick Module Tests
int xPin = A0;
int yPin = A2;
int buttonPin = 2;
int xVal;
int yVal;
int buttonState;
int waitTime = 200;
int min = 0;
int max = 1023;
int mid = 511;


void setup() {
  Serial.begin(9600);
  pinMode(xPin, INPUT);
  pinMode(yPin, INPUT);
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  xVal = analogRead(xPin);
  yVal = analogRead(yPin);
  buttonState = digitalRead(buttonPin);

  Serial.print("X: ");
  Serial.print(xVal);
  Serial.print(" | Y: ");
  Serial.print(yVal);
  Serial.print(" | Button: ");
  Serial.println(buttonState);

  delay(waitTime);
}
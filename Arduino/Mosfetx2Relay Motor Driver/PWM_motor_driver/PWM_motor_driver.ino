const int PWM_PIN = 9;

void setup() {
  pinMode(PWM_PIN, OUTPUT); 
  Serial.begin(9600);
}


void set_pwm_from_float(float float_value, int pin) {
  if (float_value > 1.0) float_value = 1.0;
  else if (float_value < -1.0) float_value = -1.0;
  
  // Map the float from [-1.0, 1.0] to [0, 255]
  // Formula: (V_float + 1.0) / 2.0 * 255
  int duty_cycle_value = round(((float_value + 1.0) / 2.0) * 255.0);
  
  analogWrite(pin, duty_cycle_value);
  
  Serial.print("Float: ");
  Serial.print(float_value, 2); 
  Serial.print(" -> Duty: ");
  Serial.println(duty_cycle_value);
}


void loop() {
  
  // Full ON (100% duty cycle)
  set_pwm_from_float(1.0, PWM_PIN); // Output: Duty ~ 255
  delay(1000); 

  // Half ON (50% duty cycle)
  set_pwm_from_float(0.0, PWM_PIN); // Output: Duty ~ 127
  delay(1000); 

  // 25% duty cycle
  set_pwm_from_float(-0.5, PWM_PIN); // Output: Duty ~ 64
  delay(1000); 

  // Full OFF (0% duty cycle)
  set_pwm_from_float(-1.0, PWM_PIN); // Output: Duty = 0
  delay(1000); 
  
  // Sweep from -1.0 to 1.0 over 10 seconds
  Serial.println("\n--- Starting Sweep ---");
  for (float i = -1.0; i <= 1.0; i += 0.05) { // Increment by 0.05
    set_pwm_from_float(i, PWM_PIN);
    delay(50); 
  }
}
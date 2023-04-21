function Arduino = StepCommandInitializeArduino()

a = arduino('COM4', 'Uno', 'Libraries', 'Adafruit/MotorShieldV2');

Arduino = a;
end
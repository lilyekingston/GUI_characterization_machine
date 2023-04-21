function Motor = StepCommandInitializeMotor(a, shield)

sm = stepper(shield, 2, 200, 'RPM',20);
writeDigitalPin(a, 'D3', 0);
writeDigitalPin(a, 'D3', 1);

Motor = sm;
end
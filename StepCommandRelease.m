function Output = StepCommandRelease(a,sm)

writeDigitalPin(a,'D5', 0);
writeDigitalPin(a,'D5', 1);
release(sm);

Output = 1;

end
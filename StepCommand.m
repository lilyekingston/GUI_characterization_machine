function output = StepCommand(dx,sm)

%dx = -10; % mm
MoveDirection = sign(dx) * 63;
move(sm, MoveDirection);

output = 1;
end
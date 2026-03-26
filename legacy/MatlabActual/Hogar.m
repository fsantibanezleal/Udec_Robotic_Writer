function y=Hogar

puerto='Com1';

%Para ubicar la base en la posicion home

Motormove(1,round(360/0.094),puerto);
Motormove(2,-round(50/0.1175),puerto);
Motormove(3,round(80/0.1175),puerto);
MotormovePR(round(60/0.458),'pitch',puerto);
pause(3)
Motormove(2,-round(12/0.1175),puerto);
parar2(puerto) ;

while 1,
    Remanentes1=CuentasRemanentes(1,puerto);
    pause(0.05);
    Remanentes1=CuentasRemanentes(1,puerto);
    pause(0.05);
    Remanentes2=CuentasRemanentes(1,puerto);
    if Remanentes1 == Remanentes2
        DetenerMotor(1,puerto);
        break;
    end
end
Motormove(1,-round(162/0.094),puerto);
MotormovePR(round(35/0.458),'pitch',puerto);

%Para ubicar gripper

Motormove(8,round(50*6.7797),puerto);
pause(0.8)
DetenerMotor(8,puerto);
pause(0.1)
Motormove(8,round(-50*6.7797),puerto);
pause(0.5)
DetenerMotor(8,puerto);
pause(0.14)
DetenerMotor(8,puerto);

%Para ubicar el hombro en la posicion home

Motormove(2,-round(200/0.1175),puerto);
while 1,
    Remanentes1=CuentasRemanentes(2,puerto);
    pause(0.2);
    Remanentes1=CuentasRemanentes(2,puerto);
    pause(0.2);
    Remanentes2=CuentasRemanentes(2,puerto);
    if Remanentes1 == Remanentes2
        DetenerMotor(2,puerto);
        break;
    end
end

Motormove(2,round(38/0.1175),puerto);
pause(2)
DetenerMotor(1,puerto);
parar2(puerto) ;
DetenerMotor(1,puerto);

% Codo

Motormove(3,round(-340/0.1175),puerto);
switch1=EstadoSwitch(3,puerto);
switch1=EstadoSwitch(3,puerto);
pause(0.4)
while 1,
    switch0=EstadoSwitch(3,puerto);
    pause(0.1);
    switch1=EstadoSwitch(3,puerto);
    pause(0.1);
    switch2=EstadoSwitch(3,puerto);
    if switch1~=switch2 || switch0~=switch2 || switch1~=switch0
        DetenerMotor(3,puerto);
        pause(1);
        break
    end
end
Motormove(3,round(-7/0.1175),puerto);
pause(0.1)
%% Pitch

MotormovePR(round(18/0.458),'pitch',puerto);
DetenerMotor(3,puerto);
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);
Ssw1=EstadoSwitch(4,puerto);
pause(0.01)
Ssw1=EstadoSwitch(4,puerto);
pause(0.01)

while 1,
    Ssw1=EstadoSwitch(4,puerto);
    pause(0.05)
    Ssw1=EstadoSwitch(4,puerto);
    if  Ssw1==31 
        DetenerMotor(4,puerto);
        DetenerMotor(5,puerto);
        break;
    end    
    MotormovePR(round(-2/0.458),'pitch',puerto);
    pause(0.05)
end

MotormovePR(round(-25/0.458),'pitch','Com1');
pause(0.5);
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);

%% Roll 
MotormovePR(round(-30/0.458),'roll',puerto);
Ssw1=EstadoSwitch(5,puerto);
pause(0.2);
Ssw1=EstadoSwitch(5,puerto);
pause(0.2);
while 1,
    Ssw1=EstadoSwitch(5,puerto);
    pause(0.05)
    Ssw1=EstadoSwitch(5,puerto);
    if  Ssw1==31 
        DetenerMotor(4,puerto);
        DetenerMotor(5,puerto);
        break;
    end    
    MotormovePR(round(2/0.458),'roll',puerto);
    pause(0.05)
end

Motormove(2,round(93/0.1175),puerto);
MotormovePR(round(18/0.458),'roll',puerto);
pause(1)
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);
MotormovePR(round(-90/0.458),'roll',puerto);

parar2(puerto) ;

    function j=parar2(puerto)   
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)
        DetenerMotor(2,puerto);
        pause(0.1)      
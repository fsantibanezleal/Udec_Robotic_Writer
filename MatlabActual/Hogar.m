function y=Hogar

puerto='Com1';

%Para ubicar la base en la posicion home

Motormove(1,-round(10/0.094),puerto);
pause(0.1)
%MotormovePR(round(7/0.458),'pitch',puerto);  
pause(0.1);
Motormove(2,-round(50/0.1175),puerto);
pause(1.3)
parar2(puerto) ;
Motormove(1,round(360/0.094),puerto);
pause(1)
Motormove(3,round(45/0.1175),puerto);
%MotormovePR(round(2/0.458),'pitch',puerto);  

while 1,
    Remanentes1=CuentasRemanentes(1,puerto);
    pause(0.2);
    Remanentes1=CuentasRemanentes(1,puerto);
    pause(0.2);
    Remanentes2=CuentasRemanentes(1,puerto);
    if Remanentes1 == Remanentes2
        DetenerMotor(1,puerto);
        break;
    end
end
Motormove(1,-round(164.5/0.094),puerto);
%MotormovePR(round(2/0.458),'pitch',puerto);

pause(8)
DetenerMotor(1,puerto);


%Para ubicar el hombro en la posicion home

Motormove(2,-round(200/0.1175),puerto);
%MotormovePR(round(5/0.458),'pitch',puerto);
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

Motormove(2,round(45/0.1175),puerto);
Motormove(3,round(40/0.1175),puerto);
%MotormovePR(round(4/0.458),'pitch',puerto);
pause(2)
DetenerMotor(1,puerto);
parar2(puerto) ;
Motormove(3,round(17/0.1175),puerto);
%MotormovePR(round(7/0.458),'pitch',puerto);
% Codo

pause(1);
Motormove(3,round(-300/0.1175),puerto);
%MotormovePR(round(1/0.458),'pitch',puerto);
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
        pause(2);
        break
    end
end
Motormove(3,round(-6.5/0.1175),puerto);

%% Pitch

%MotormovePR(round(17/0.458),'pitch',puerto);
pause(1.7);
DetenerMotor(3,puerto);
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);
Ssw1=EstadoSwitch(4,puerto);
pause(0.01)
Ssw1=EstadoSwitch(4,puerto);
pause(0.01)

while 1,
    Ssw1=EstadoSwitch(4,puerto);
    pause(0.1)
    Ssw1=EstadoSwitch(4,puerto);
    if  Ssw1==31 
        DetenerMotor(4,puerto);
        DetenerMotor(5,puerto);
        break;
    end    
    %MotormovePR(round(-2/0.458),'pitch',puerto);
    pause(0.1)
end

%MotormovePR(round(-34/0.458),'pitch','Com1');
pause(1);
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);

%% Roll 
%MotormovePR(round(-30/0.458),'roll',puerto);
Ssw1=EstadoSwitch(5,puerto);
pause(0.9);
Ssw1=EstadoSwitch(5,puerto);
pause(0.9);
while 1,
    Ssw1=EstadoSwitch(5,puerto);
    pause(0.1)
    Ssw1=EstadoSwitch(5,puerto);
    if  Ssw1==31 
        DetenerMotor(4,puerto);
        DetenerMotor(5,puerto);
        break;
    end    
    %MotormovePR(round(2/0.458),'roll',puerto);
    pause(0.3)
end

%MotormovePR(round(18/0.458),'roll',puerto);
pause(1)
DetenerMotor(4,puerto);
DetenerMotor(5,puerto);

Motormove(8,round(50*6.7797),puerto);
pause(0.8)
DetenerMotor(8,puerto);
pause(0.2)
Motormove(8,round(-50*6.7797),puerto);
pause(0.5)
DetenerMotor(8,puerto);

%% Efector

pause(0.14)
DetenerMotor(8,puerto);
parar2(puerto) ;




    function j=parar2(puerto)   
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);
        pause(0.17)
        DetenerMotor(2,puerto);


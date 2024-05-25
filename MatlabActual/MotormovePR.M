function [inf]=MotormovePR(pasos,tipo,puerto)

motor4=4;
motor5=5;
pasos4=pasos;        

switch tipo
    case 'pitch'
        pasos5=-pasos4;
    case 'roll'
        pasos5=pasos4;
end

% Sentido de giro del motor 4

    if pasos4 >= 0,
		sentido4 = '+';
	else
		sentido4 = '-';
    end

% Sentido de giro del motor 5
    if pasos5 >= 0,
		sentido5 = '+';
	else
		sentido5 = '-';
    end
   
% Genera el String de comando Motor 4
    pasos=abs(pasos4);
    Udemil=fix(pasos./1000);
	pasos=rem(pasos,1000);
	Centenas=fix(pasos./100);
	pasos=rem(pasos,100);
	Decenas=fix(pasos./10);
    Unidades=rem(pasos,10);

mensajeMotor4=[ int2str(abs(int2str(motor4))) ',' int2str(abs('M')) ',' int2str(abs(sentido4)) ',' int2str(abs(int2str(Udemil))) ',' int2str(abs(int2str(Centenas))) ',' int2str(abs(int2str(Decenas))) ',' int2str(abs(int2str(Unidades))) ',13' ];
mensajeMotor5=[ int2str(abs(int2str(motor5))) ',' int2str(abs('M')) ',' int2str(abs(sentido5)) ',' int2str(abs(int2str(Udemil))) ',' int2str(abs(int2str(Centenas))) ',' int2str(abs(int2str(Decenas))) ',' int2str(abs(int2str(Unidades))) ',13' ];

mensajeGet=[ '' '[SENDOUT(' mensajeMotor4 ',' mensajeMotor5 ')]' '' ];
mensajeGet = mat2str(mensajeGet);	


% Inicializa comunicación DDE con Winwedge
	canal = ddeinit('winwedge',puerto);
% Envia mensaje a la puerta serial
	retorno = ddeexec(canal,mensajeGet);
%  Fin de la comunicacion dde
	retorno = ddeterm(canal);
% Fin de transmmision de movimiento
	inf  = retorno;

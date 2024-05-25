function [inf]=Motormove(motor,pasos,puerto)
%
%

% Redondeo de pasos
    pasos=round(pasos);

% verificacion de sentido de desplazamiento
	if  pasos >= 0,
        sentido = '+';
	else
		sentido = '-';
    end

% Restringimos el numero de pasos al maximo de 4 cifras que se pueden
% enviar en el formato del brazo
    pasos=abs(pasos);
    if pasos > 9999
        pasos = 9999;
    end

% Covertimos el numero de pasos a los caracteres que seran enviados en el
% mensaje

	Udemil=fix(pasos./1000);
	pasos=rem(pasos,1000);
	Centenas=fix(pasos./100);
	pasos=rem(pasos,100);
	Decenas=fix(pasos./10);
    Unidades=rem(pasos,10);

% Codificacion del mensaje en el formato de comunicacion con el brazo
    mensajeMotor=[ int2str(abs(int2str(motor))) ',' int2str(abs('M')) ',' int2str(abs(sentido)) ',' int2str(abs(int2str(Udemil))) ',' int2str(abs(int2str(Centenas))) ',' int2str(abs(int2str(Decenas))) ',' int2str(abs(int2str(Unidades))) ',13'];
    mensajeGet=['[SENDOUT(' mensajeMotor ')]'];
    mensajeGet = mat2str(mensajeGet);	

% Inicializa comunicación DDE con Winwedge
	canal = ddeinit('winwedge',puerto);
% Envia mensaje a la puerta serial
	retorno = ddeexec(canal,mensajeGet);
%  Fin de la comunicacion dde
	retorno = ddeterm(canal);
% Fin de transmmision de movimiento
	inf  = retorno;


% Detemer movimiento de motor
function [inf]=DetenerMotor(Motor,puerto)

% Genera el String de comando
    mensajeGet  = ['[SENDOUT(' int2str(abs(int2str(Motor))) ',' int2str(abs('P')) ',13)]'];
    mensajeGet = mat2str(mensajeGet);	
% Inicializa comunicación con Winwedge
	canal  = ddeinit('winwedge',puerto);
% Envia mensaje a puerta serial
	retorno   = ddeexec(canal,mensajeGet);
% Espera recepción del mensaje de respuesta
	deten  = ddereq(canal,'Field(1)');
% Termina comunicacion dde
	retorno   = ddeterm(canal);
% fin
	inf  = deten;

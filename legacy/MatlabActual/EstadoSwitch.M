function [info]=EstadoSwitch(motor,puerto)

% Genera el String de comando
    mensajeSwitch = ['' '[SENDOUT(' int2str(abs(int2str(motor))) ',' int2str(abs('L')) ',13)]' ''];
	mensajeSwitch = mat2str(mensajeSwitch);
% Inicializa comunicación con Winwedge
	canal  = ddeinit('winwedge',puerto);
% Envia mensaje a puerta serial
	retorno   = ddeexec(canal,mensajeSwitch);
% Espera recepción del mensaje de respuesta
	Estado  = ddereq(canal,'Field(1)');
% Termina comunicacion dde
	retorno   = ddeterm(canal);
% fin
	info  = Estado;

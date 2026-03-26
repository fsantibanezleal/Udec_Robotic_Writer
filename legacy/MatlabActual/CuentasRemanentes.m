function info= CuentasRemanentes(motor,puerto)

% Genera el String de comando
mensajeMotor=[ int2str(abs(int2str(motor))) ',' int2str(abs('Q')) ',13'];
mensajeGet=[ ''  '[SENDOUT(' mensajeMotor ')]'  '' ];
mensajeGet = mat2str(mensajeGet);	

% mensajeSwitch = ['[SENDOUT(' int2str(abs(int2str(motor))) ',' int2str(abs('L')) ',13)]'];
% 	mensajeSwitch = mat2str(mensajeSwitch)


% Inicializa comunicación con Winwedge
        canal = ddeinit('winwedge',puerto);
% Envia mensaje a puerta serial
        retorno = ddeexec(canal,mensajeGet);
        cuentas = ddereq(canal,'Field(1)',[1 1]);
        if(length(cuentas)~=2)
            'error en cuentas';
            cuentas='00';
        end
        info = dec2bin(hex2dec(cuentas));
        info = pad(info);
% Termina comunicacion dde
        retorno = ddeterm(canal);

    function y=pad(str)
        L = length(str);
        L = 16-L;
        for i=1:L
            str=['0' str];
        end
        signo = str(2);
        num = [str(3:8) str(10:16)];
        if(signo=='1')
            for i=1:13
                if(num(i)=='1')
                    num(i)='0';
                else 
                    num(i)='1';
                end
            end
        end
        y= bin2dec(num);
        
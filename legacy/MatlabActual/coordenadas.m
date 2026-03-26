function coordenadas
M = 0;
T=zeros(1,5);
k = 1;
op = 0;

while M < 3
    M = menu('Que hacer?', 'Ingresar coordenadas', 'Home','Salir');
    
    switch(M)
        case 1
            x = inputdlg('Ingrese coordenada para el eje X =');
            X = str2double(x);
            y = inputdlg('Ingrese coordenada para el eje Y =');
            Y = str2double(y);
            z = inputdlg('Ingrese coordenada para el eje Z =');
            Z = str2double(z);
            
        case 2
            X = 456;
            Y = 0;
            Z = 189;
            op = 0;
            
        case 3
            break
    end
    POSICION = [1 0 0 X 0 -1 0 Y 0 0 -1 Z zeros(1,3) 1];
    
    p_inverso;
end
palabra=handlesdealgo;
Extension=length(palabra);
for i=1:Extension,
    LetraActual=palabra(i);
    LetraActual=double(LetraActual)-64;
    if(LetraActual == -32)
        handles.posicion(i)=0;
    elseif (LetraActual < 33)
        handles.posicion(i)=LetraActual;
        if(LetraActual > 14)
            handles.posicion(i)=handles.posicion(i)+1;
        end
    elseif(LetraActual < 58)
        handles.posicion(i)=LetraActual-32;
        if(LetraActual > 14+33)
            handles.posicion(i)=LetraActual-32;
        end
    elseif(LetraActual == 145 || LetraActual == 177 )
        handles.posicion(i)=15;
    elseif(LetraActual == 161 || LetraActual == 129)
        handles.posicion(i)=1;
    elseif(LetraActual == 169 || LetraActual == 137)
        handles.posicion(i)=2;
    elseif(LetraActual == 173 || LetraActual == 141)
        handles.posicion=3;
    elseif(LetraActual == 179 || LetraActual == 147)
        handles.posicion(i)=4;
    elseif(LetraActual == 186 || LetraActual == 154)
        handles.posicion(i)=5;
    end
        imprimir....
end
    
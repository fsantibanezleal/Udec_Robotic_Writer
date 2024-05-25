palabra=handlesdealgo;
Extension=length(palabra);
for i=1:Extension,
    LetraActual=palabra(i);
    LetraActual=double(LetraActual)-64;
    if(LetraActual == -32)
        uno(i)=0;
    elseif (LetraActual < 33)
        uno(i)=LetraActual;
        if(LetraActual > 14)
            uno(i)=uno(i)+1;
        end
    elseif(LetraActual < 58)
        uno(i)=LetraActual-32;
        if(LetraActual > 14+33)
            uno(i)=LetraActual-32;
        end
    elseif(LetraActual == 145 || LetraActual == 177 )
        uno(i)=15;
    elseif(LetraActual == 161 || LetraActual == 129)
        uno(i)=1;
    elseif(LetraActual == 169 || LetraActual == 137)
        uno(i)=2;
    elseif(LetraActual == 173 || LetraActual == 141)
        uno(i)=3;
    elseif(LetraActual == 179 || LetraActual == 147)
        uno(i)=4;
    elseif(LetraActual == 186 || LetraActual == 154)
        uno(i)=5;
    end
end
    
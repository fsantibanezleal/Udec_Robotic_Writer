alpha1  =-pi/2; 
d1		= 340;
a1		= 16;

alpha2  = 0;
d2		= 0;
a2		= 220;

alpha3  = 0;
d3		= 0;
a3		= 220;

alpha4  =-pi/2;
d4		= 0;
a4		= 0;

alpha5=0;     
d5		= 151;
a5		= 0;

P = questdlg('Desea movimiento real del brazo','Brazo Robótico','Si','No','No');
if P == 'Si'
    sw = 1;
else
    sw = 0;
end

for i=1:length(POSICION(:,1))
    
    T5 = traduccion(POSICION(i,:));
    op = opr(i);
    
    % problema inverso
    % mantiene la orientacion actual
    ux=T5(1,1); uy=T5(2,1); uz=T5(3,1);
    vx=T5(1,2); vy=T5(2,2); vz=T5(3,2);
    wx=T5(1,3); wy=T5(2,3); wz=T5(3,3);

    % ingresa nueva posicion del efector
    qx=T5(1,4);
    qy=T5(2,4);
    qz=T5(3,4);

    % Calculo del theta1
    theta(1)=atan(qy/qx);
    
    %Calculo del theta5
    theta(5)=asin(ux*sin(theta(1))-uy*cos(theta(1)));
    
    %Calculo del theta3
    theta234=atan2((-uz/cos(theta(5))),((ux*cos(theta(1))+uy*sin(theta(1)))/cos(theta(5))));
    k1=qx*cos(theta(1))+qy*sin(theta(1))-a1+d5*sin(theta234);
    k2=-qz+d1-d5*cos(theta234);
    theta(3)=acos((k1^2+k2^2-a2^2-a3^2)/(2*a2*a3));
    
    % Calculo de theta2
    cost2=(k1*(a2+a3*cos(theta(3)))+k2*a3*sin(theta(3)))/(a2^2+a3^2+2*a2*a3*cos(theta(3)));
    sint2=(-k1*a3*sin(theta(3))+k2*(a2+a3*cos(theta(3))))/(a2^2+a3^2+2*a2*a3*cos(theta(3)));
    theta(2)=atan2(sint2,cost2);
    
    % Calculo de theta4
    theta(4)=theta234-theta(2)-theta(3);
    t = T;
    T = theta*180/pi;
    t = T - t;
    % Grafica usando problema directo
    aux = dibujar(t,theta,op,sw);
    clear aux;
    
    pause(2)
    if any(abs(t)>= 30)
        pause(4)
    end
end
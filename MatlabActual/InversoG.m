function [theta1,theta2,theta3,theta4,theta5]=InversoG(T5,puerto)

        l1			=16;
        l2			=220;
        l3			=220;
        
        alpha1  =-pi/2; 
        d1		= 340;
        a1		= l1;

        alpha2  = 0;
        d2		= 0;
        a2		= l2;

        alpha3  = 0;
        d3		= 0;
        a3		= l3;
        
        alpha4  =-pi/2;
        d4		= 0;
        a4		= 0;
        
        alpha5=0;     
        d5		= 151;
        a5		= 0;
    % problema inverso
    % mantiene la orientacion actual
        ux=T5(1,1); uy=T5(2,1); uz=T5(3,1);
        vx=T5(1,2); vy=T5(2,2); vz=T5(3,2);
        wx=T5(1,3); wy=T5(2,3); wz=T5(3,3);
        qx=T5(1,4); qy=T5(2,4); qz=T5(3,4);
        
    % Calculo del theta1
        theta1=atan(qy/qx)
        if ( (sign(qy) == 1) && (sign(qx)==-1))
            theta1=pi/2+(pi/2-abs(theta1));
        elseif( (sign(qy) == -1) && (sign(qx)==-1))
            theta1=-(pi/2+(pi/2-abs(theta1)));
        end
    %Calculo del theta5
        inter=ux*sin(theta1)-uy*cos(theta1);
        if (inter > 1)
            inter=1;
        end
        if (inter < -1)
            inter=-1;
        end
        theta5=asin(inter);
    %Calculo del theta3
        theta234=atan2((-uz/cos(theta5)),((ux*cos(theta1)+uy*sin(theta1))/cos(theta5)))
        k1=qx*cos(theta1)+qy*sin(theta1)-a1+d5*sin(theta234);
        k2=-qz+d1-d5*cos(theta234);
        inter2=(k1^2+k2^2-a2^2-a3^2)/(2*a2*a3);
        if (inter2 > 1)
            inter2=1;
        end
        if (inter2 < -1)
            inter2=-1;
        end
        theta3=acos(inter2);
    % Calculo de theta2
        cost2=(k1*(a2+a3*cos(theta3))+k2*a3*sin(theta3))/(a2^2+a3^2+2*a2*a3*cos(theta3));
        sint2=(-k1*a3*sin(theta3)+k2*(a2+a3*cos(theta3)))/(a2^2+a3^2+2*a2*a3*cos(theta3));
        theta2=atan2(sint2,cost2);
    % Calculo de theta4
        theta4=theta234-theta2-theta3;

        
        theta1=theta1*180/pi;
        theta2=theta2*180/pi;
        theta3=theta3*180/pi;
        theta4=theta4*180/pi;
        theta5=theta5*180/pi;

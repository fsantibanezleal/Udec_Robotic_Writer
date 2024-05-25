function [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,Ejecutar,puerto,ang1Ant,ang2Ant,ang3Ant,ang4Ant,ang5Ant,opAnt)

%   El siguiente codigo permite obtener el resultado del problema directo
    
%   Ingresar angulos de desplazamiento de todas las piezas en relacion a
%   home
%     ang1		=input(' ingrese angulo base   (grad) =');
%     ang2		=input(' ingrese angulo hombro (grad) =');
    ang2=ang2-90;
    ang2Ant=ang2Ant-90;
%     ang3		=input(' ingrese angulo codo   (grad) =');
    ang3		=ang3-ang2;
    ang3Ant		=ang3Ant-ang2Ant;
%     ang4		=input(' ingrese angulo pitch  (grad) =');
    ang4		=ang4-ang3-ang2;
    ang4Ant		=ang4Ant-ang3Ant-ang2Ant;
%     ang5		=input(' ingrese angulo roll   (grad) =');
%     op			=input(' ingrese abertura (mm) =');
%     Ejecutar    =input(' Operacion(0:Simulacion/1:Ejecucion)  =');

    theta1	=(ang1*pi)/180;
    theta2	=(ang2*pi)/180;
    theta3	=(ang3*pi)/180;
    theta4	=(ang4*pi)/180;
    ang5    =ang5-90;
    ang5Ant =ang5Ant-90;
    theta5	=(ang5*pi)/180;

    l1			=16;
    l2			=220;
    l3			=220;

%   Matriz de la relacion existente entre base y hombro
    alpha1  = -pi/2;
    d1		= 340;
    a1		= l1;
    A1=[    cos(theta1)  -cos(alpha1)*sin(theta1)	  	sin(alpha1)*sin(theta1) 	a1*cos(theta1)  ;
            sin(theta1)   cos(alpha1)*cos(theta1)       -sin(alpha1)*cos(theta1) 	a1*sin(theta1)  ;
                0		          sin(alpha1)	                cos(alpha1)              d1         ;
                0		              0                              0                    1		]   ;

    if Ejecutar == 1,
        st=Motormove(1,round((ang1-ang1Ant)/0.094),puerto);
    end  
    
%   Matriz de la relacion existente entre hombro y codo
    alpha2  = 0;
    d2		= 0;
    a2		= l2;
    A2=[    cos(theta2)  -cos(alpha2)*sin(theta2)	  	sin(alpha2)*sin(theta2) 	a2*cos(theta2)  ;
            sin(theta2)   cos(alpha2)*cos(theta2)       -sin(alpha2)*cos(theta2) 	a2*sin(theta2)  ;
                0		          sin(alpha2)	                cos(alpha2)             d2          ;
                0		              0                              0                  1		]   ;
      
    if Ejecutar == 1,
        st=Motormove(2,round((ang2-ang2Ant)/0.1175),puerto);
    end 
     
%   Matriz de la relacion existente entre codo y muñeca
    alpha3  = 0;
    d3		= 0;
    a3		= l2;
    A3=[    cos(theta3)  -cos(alpha3)*sin(theta3)	  	sin(alpha3)*sin(theta3) 	a3*cos(theta3)  ;
            sin(theta3)   cos(alpha3)*cos(theta3)       -sin(alpha3)*cos(theta3) 	a3*sin(theta3)  ;
                0		          sin(alpha3)	                cos(alpha3)             d3          ;
                0		              0                             0                   1		]   ;
    if Ejecutar == 1,
        st=Motormove(3,round(-(ang2+ang3-(ang2Ant+ang3Ant))/0.1175),puerto);
    end 

% Matriz relacionada con el pitch
    alpha4  = -pi/2;
    d4		= 0;
    a4		= 0;
    A4=[    cos(theta4)  -cos(alpha4)*sin(theta4)	  	sin(alpha4)*sin(theta4) 	a4*cos(theta4)  ;
            sin(theta4)   cos(alpha4)*cos(theta4)       -sin(alpha4)*cos(theta4) 	a4*sin(theta4)  ;
                0               sin(alpha4)                     cos(alpha4)             d4          ;
                0                   0                               0                   1		]   ;

    if Ejecutar == 1,
        st=MotormovePR(round((ang4-ang4Ant)/0.458) ,'pitch',puerto);
    end 

% Matriz relacionada con el roll y el gripper
    alpha5  = 0;     
    d5		= 151;
    a5		= 0;
    A5=[    cos(theta5)  -cos(alpha5)*sin(theta5)	  	sin(alpha5)*sin(theta5)     a5*cos(theta5)  ;
            sin(theta5)   cos(alpha5)*cos(theta5)       -sin(alpha5)*cos(theta5) 	a5*sin(theta5)  ;
                0               sin(alpha5)                     cos(alpha5)             d5          ;
                0                   0                               0                    1		]   ;
            
    if Ejecutar == 1,
        st=MotormovePR(round((ang5-ang5Ant)/0.458),'roll' ,puerto);
    end 
    if Ejecutar == 1,
        st=Motormove(8,round(-(op-opAnt)*6.7797),puerto);
    end 
     
% Calculo de vector de posicion. 
    T5=A1*A2*A3*A4*A5;
    T4=A1*A2*A3*A4;
    T3=A1*A2*A3;
    T2=A1*A2;
    T1=A1;

    
    
    x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
    y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
    z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];
 
%     Dibujar(x,y,z);
% 
%     DibBase;
%     Hombro(A1)
%     CyM(A1*A2) 
%     CyM(A1*A2*A3)
%     Gripper(A1*A2*A3*A4*A5,op)     

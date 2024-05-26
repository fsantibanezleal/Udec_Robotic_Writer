% Solución Problema Directo Robot Scorbot III
% parámetros del brazo robótico
clear;
t1			=input(' ingrese base  (theta1[grad]) =');
t2			=input(' ingrese hombro(theta2[grad]) =');
t3			=input(' ingrese codo  (theta3[grad]) =');
t3			=t3-t2;
t4			=input(' ingrese pitch (theta4[grad]) =');
t4			=t4-t3-t2;
t5          =input(' ingrese roll  (theta5[grad]) =');
op			=input(' ingrese abertura gripper(mm) =');
sw			=input(' Movimiento brazo(0:no/1:si)  =');

theta1	=t1*pi/180;
theta2	=t2*pi/180;
theta3	=t3*pi/180;
theta4	=t4*pi/180;
theta5	=t5*pi/180;

l1			=16;
l2			=220;
l3			=220;

%base  %dibuja la base del manipulador

% matriz del hombro respecto a base
alpha1=-pi/2;
d1		= 340;
a1		= l1;
A1=[ cos(theta1)    -cos(alpha1)*sin(theta1)    sin(alpha1)*sin(theta1)     a1*cos(theta1);
     sin(theta1)    cos(alpha1)*cos(theta1)     -sin(alpha1)*cos(theta1) 	a1*sin(theta1);
	 0		        sin(alpha1)	                cos(alpha1)                 d1;
	 0		        0	                        0                           1		];
%shoulder(A1)
if sw == 1,
   st=sendmov(1,round(t1/0.094),'Com1')
end    
% Matriz del codo respecto a hombro
alpha2= 0;
d2		= 0;
a2		= l2;
A2=[ cos(theta2)  -cos(alpha2)*sin(theta2)	  	sin(alpha2)*sin(theta2) 	a2*cos(theta2);
     sin(theta2)   cos(alpha2)*cos(theta2)     -sin(alpha2)*cos(theta2) 	a2*sin(theta2);
	     0		          sin(alpha2)	                cos(alpha2)    		d2;
   	  0		              0	                          0		         1		];
%Link1(A1*A2)       
if sw == 1,
   st=sendmov(2,round(t2/0.1175),'Com1')
end 
% Matriz muñeca respecto al codo
alpha3= 0;
d3		= 0;
a3		= l2;
A3=[ cos(theta3)  -cos(alpha3)*sin(theta3)	  	sin(alpha3)*sin(theta3) 	a3*cos(theta3);
     sin(theta3)   cos(alpha3)*cos(theta3)     -sin(alpha3)*cos(theta3) 	a3*sin(theta3);
	     0		          sin(alpha3)	                cos(alpha3)    		d3;
   	  0		              0	                          0		         1		];
%Link2(A1*A2*A3)
if sw == 1,
   st=sendmov(3,round(-(t2+t3)/0.1175),'Com1')
end 

% Matriz Muñeca (pitch)
 alpha4=  -pi/2;
 d4		= 0;
 a4		= 0;
 A4=[ cos(theta4)  -cos(alpha4)*sin(theta4)	  	sin(alpha4)*sin(theta4) 	a4*cos(theta4);
      sin(theta4)   cos(alpha4)*cos(theta4)     -sin(alpha4)*cos(theta4) 	a4*sin(theta4);
	     0		          sin(alpha4)	                cos(alpha4)    		d4;
   	  0		              0	                          0		         1		];
if sw == 1,
   st=sendm45(round((t4)/0.458),round(-(t4)/0.458) ,'Com1')
end 

% Matriz Muñeca (roll) a Gripper
alpha5=0;     
d5		= 151;
a5		= 0;
A5=[ cos(theta5)  -cos(alpha5)*sin(theta5)	  	sin(alpha5)*sin(theta5) 	a5*cos(theta5);
    sin(theta5)   cos(alpha5)*cos(theta5)     -sin(alpha5)*cos(theta5) 	   a5*sin(theta5);
	     0		          sin(alpha5)	                cos(alpha5)    		d5;
   	  0		              0	                          0		         1		];
if sw == 1,
   st=sendm45(round(t5/0.458),round(t5/0.458) ,'Com1')
end 

%Gripper(A1*A2*A3*A4*A5,op)     
     
% Calculo de vector de posicion. 
T5=A1*A2*A3*A4*A5
T4=A1*A2*A3*A4;
T3=A1*A2*A3;
T2=A1*A2;
T1=A1;

 x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
 y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
 z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];
 
 view([112.5,30])
 plot3(x,y,z),
 grid on

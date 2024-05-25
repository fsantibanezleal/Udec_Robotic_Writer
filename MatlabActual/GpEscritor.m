function varargout = Gpdirecto(varargin)


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%INICIALIZAR%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    % GPDIRECTO M-file for Gpdirecto.fig
    %      GPDIRECTO, by itself, creates a new GPDIRECTO or raises the existing
    %      singleton*.
    %
    %      H = GPDIRECTO returns the handle to a new GPDIRECTO or the handle to
    %      the existing singleton*.
    %
    %      GPDIRECTO('CALLBACK',hObject,eventData,handles,...) calls the local
    %      function named CALLBACK in GPDIRECTO.M with the given input arguments.
    %
    %      GPDIRECTO('Property','Value',...) creates a new GPDIRECTO or raises the
    %      existing singleton*.  Starting from the left, property value pairs are
    %      applied to the GUI before Gpdirecto_OpeningFunction gets called.  An
    %      unrecognized property name or invalid value makes property application
    %      stop.  All inputs are passed to Gpdirecto_OpeningFcn via varargin.
    %
    %      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
    %      instance to run (singleton)".
    %
    % See also: GUIDE, GUIDATA, GUIHANDLES
    
    % Edit the above text to modify the response to help Gpdirecto

    % Last Modified by GUIDE v2.5 28-Oct-2007 15:32:23

    % Begin initialization code - DO NOT EDIT

    gui_Singleton = 1;
    gui_State = struct('gui_Name',       mfilename, ...
                       'gui_Singleton',  gui_Singleton, ...
                       'gui_OpeningFcn', @Gpdirecto_OpeningFcn, ...
                       'gui_OutputFcn',  @Gpdirecto_OutputFcn, ...
                       'gui_LayoutFcn',  [] , ...
                       'gui_Callback',   []);
    if nargin & isstr(varargin{1})
        gui_State.gui_Callback = str2func(varargin{1});
    end

    if nargout
        [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
    else
        gui_mainfcn(gui_State, varargin{:});
    end

    % End initialization code - DO NOT EDIT


    global  T1;
    global  T2;
    global  T3;
    global  T4;
    global  T5;
    global  ang1;
    global  ang2;
    global  ang3;
    global  ang4;
    global  ang5;
    global  op;


    % --- Executes just before Gpdirecto is made visible.
    
    function Gpdirecto_OpeningFcn(hObject, eventdata, handles, varargin)
    % This function has no output args, see OutputFcn.
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)
    % varargin   command line arguments to Gpdirecto (see VARARGIN)

    %Colocar Imagen de fondo
    back= imread('fondo.jpg'); %Leer imagen
    axes(handles.back); %Carga la imagen en background
    axis off;
    imshow(back); %Presenta la imagen

    angulos= imread('angulos.jpg'); %Leer imagen
    axes(handles.angulos); %Carga la imagen en background
    axis off;
    imshow(angulos); %Presenta la imagen
  
    
    archivar= imread('archivar.jpg'); %Leer imagen
    axes(handles.archivar); %Carga la imagen en background
    axis off;
    imshow(archivar); %Presenta la imagen

    
    delete('Posiciones.txt');
    handles.Archivo = fopen('Posiciones.txt','wb');

    handles.output = hObject;
    % Update handles structure
    guidata(hObject, handles);

    %Colocar Imagen brazo
    op=50;
    handles.Base=0;
    handles.Hombro=0;
    handles.Codo=0;
    handles.Pitch=0;
    handles.Roll=0;
    handles.Apertura=op; %op
    handles.BaseAnt=0;
    handles.HombroAnt=0;
    handles.CodoAnt=0;
    handles.PitchAnt=0;
    handles.RollAnt=0;
    handles.AperturaAnt=op; %op
    puerto='Com1';
    
    guidata(hObject,handles);
    %% Movemos solo por seguridad... no seguridad del sistema sino para
    %% asegurar estar en home-.... jajajaja POR ESO DEBE SER    .... op,1,puerto....
    [d1,A1,A2,A3,A4,A5]=DirectoG(0,0,0,0,0,op,0,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
        T5=A1*A2*A3*A4*A5;
        T4=A1*A2*A3*A4;
        T3=A1*A2*A3;
        T2=A1*A2;
        T1=A1;
    
        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];
    axes(handles.Brazo); %Carga la imagen  
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
    axes(handles.Brazo1); %Carga la imagen    
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
    axes(handles.Brazo2); %Carga la imagen   
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);        
    axes(handles.Brazo3); %Carga la imagen   
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    Stop(puerto);
    
    handles.Archivo = fopen('Posiciones.txt','wb');
    % Choose default command line output for Gpdirecto
    handles.output = hObject;
    
    % Update handles structure
    guidata(hObject, handles);

    % UIWAIT makes Gpdirecto wait for user response (see UIRESUME)
    % uiwait(handles.figure1);


    % --- Outputs from this function are returned to the command line.
    function varargout = Gpdirecto_OutputFcn(hObject, eventdata, handles)
    % varargout  cell array for returning output args (see VARARGOUT);
    % hObject    handle to figure
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)

    % Get default command line output from handles structure
    varargout{1} = handles.output;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%FIN INICIALIZAR%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Edits%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Creacion%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % --- Executes during object creation, after setting all properties.
    function Base_CreateFcn(hObject, eventdata, handles)
    % hObject    handle to Base (see GCBO)
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    empty - handles not created until after all CreateFcns called
    
    % Hint: edit controls usually have a white back on Windows.
    %       See ISPC and COMPUTER.
       if ispc
            set(hObject,'BackgroundColor','white');
       else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
       end

    function Hombro_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

    function Codo_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
    
    function Pitch_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Roll_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Apertura_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end
        
    function Puerto_CreateFcn(hObject, eventdata, handles)
        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

    function nombrearchivo_CreateFcn(hObject, eventdata, handles)

        if ispc
            set(hObject,'BackgroundColor','white');
        else
            set(hObject,'BackgroundColor',get(0,'defaultUicontrolBackgroundColor'));
        end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Llamado%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    function Base_Callback(hObject, eventdata, handles)
        % hObject    handle to Base (see GCBO)
        % eventdata  reserved - to be defined in a future version of MATLAB
        % handles    structure with handles and user data (see GUIDATA)

        % Hints: get(hObject,'String') returns contents of Base as text
        %        str2double(get(hObject,'String')) returns contents of Base as a double

        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -126.5 )
            NewVal=-126.5;
        elseif ( NewVal > 126.5 )
            NewVal=126.5;
        end
        handles.Base=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Hombro_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -53.7 )
            NewVal=-53.7;
        elseif ( NewVal > 126.5 )
            NewVal=126.5;
        end     
        handles.Hombro=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Codo_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -27.8 )
            NewVal=-27.8;
        elseif ( NewVal > 77.7 )
            NewVal=77.7;
        end
        handles.Codo=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Pitch_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -250 )
            NewVal=-250;
        elseif ( NewVal > 77.7 )
            NewVal=77.7;
        end
        handles.Pitch=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Roll_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < -180 )
            NewVal=-180;
        elseif ( NewVal > 180 )
            NewVal=180;
        end
        handles.Roll=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);
        
    function Apertura_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        if ( NewVal < 0 )
            NewVal= 0;
        elseif ( NewVal > 59 )
            NewVal= 59;
        end
        handles.Apertura=NewVal; %Almacenar en puntero
        handles.output = hObject;
        guidata(hObject, handles);

    function Puerto_Callback(hObject, eventdata, handles)
        NewStrVal=get(hObject,'String'); %Almacenar valor ingresado
        NewVal = str2double(NewStrVal); %Transformar a formato double
        handles.Port=NewVal
        handles.output = hObject;
        guidata(hObject, handles);


    function nombrearchivo_Callback(hObject, eventdata, handles)
        handles.output = hObject;
        guidata(hObject, handles);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Fin Edits%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Push Buttons%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % --- Executes on button press in pushbutton1. Ejecutar
    function pushbutton1_Callback(hObject, eventdata, handles)
    % hObject    handle to pushbutton1 (see GCBO)
    % eventdata  reserved - to be defined in a future version of MATLAB
    % handles    structure with handles and user data (see GUIDATA)

        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        puerto=handles.port;
        op=handles.Apertura;

    % Choose default command line output for Gpdirecto
        handles.output = hObject;
    
    % Update handles structure
        guidata(hObject, handles);

    %Colocar Imagen brazo
        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
            T5=A1*A2*A3*A4*A5;
            T4=A1*A2*A3*A4;
            T3=A1*A2*A3;
            T2=A1*A2;
            T1=A1;

            x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
            y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
            z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];

        handles.BaseAnt=handles.Base;
        handles.HombroAnt=handles.Hombro;
        handles.CodoAnt=handles.Codo;
        handles.PitchAnt=handles.Pitch;
        handles.RollAnt=handles.Roll;
        handles.AperturaAnt=handles.Apertura;

    % Choose default command line output for Gpdirecto
        handles.output = hObject;
    
    % Update handles structure
        guidata(hObject, handles);
    
        axes(handles.Brazo); %Carga la imagen en background
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        axes(handles.Brazo2); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        handles.output = hObject;
        guidata(hObject, handles);
        Stop(puerto);
    % --- Executes on button press in pushbutton2.Simular
    function pushbutton2_Callback(hObject, eventdata, handles)
        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        puerto=handles.port;
        op=handles.Apertura;
        handles.output = hObject;
        guidata(hObject, handles);

        %Colocar Imagen brazo
        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,0,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
            T5=A1*A2*A3*A4*A5;
            T4=A1*A2*A3*A4;
            T3=A1*A2*A3;
            T2=A1*A2;
            T1=A1;

        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];

        % Choose default command line output for Gpdirecto
            handles.output = hObject;

        % Update handles structure
            guidata(hObject, handles);

            axes(handles.Brazo); %Carga la imagen en background
            pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
            pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        axes(handles.Brazo2); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
    % --- Executes on button press in Resetear.
    function Resetear_Callback(hObject, eventdata, handles)
        op=50;
        handles.Base=0;
        handles.Hombro=0;
        handles.Codo=0;
        handles.Pitch=0;
        handles.Roll=0;
        handles.Apertura=op; %op
        guidata(hObject,handles);

        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        puerto=handles.port;
        op=handles.Apertura;

        % Choose default command line output for Gpdirecto
            handles.output = hObject;

        % Update handles structure
            guidata(hObject, handles);

        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,1,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
                T5=A1*A2*A3*A4*A5;
                T4=A1*A2*A3*A4;
                T3=A1*A2*A3;
                T2=A1*A2;
                T1=A1;

        x=[ 0 0  T1(1,4) T2(1,4) T3(1,4) T4(1,4) T5(1,4)];  
        y=[ 0 0  T1(2,4) T2(2,4) T3(2,4) T4(2,4) T5(2,4)];
        z=[ 0 d1 T1(3,4) T2(3,4) T3(3,4) T4(3,4) T5(3,4)];


        handles.BaseAnt=handles.Base;
        handles.HombroAnt=handles.Hombro;
        handles.CodoAnt=handles.Codo;
        handles.PitchAnt=handles.Pitch;
        handles.RollAnt=handles.Roll;
        handles.AperturaAnt=handles.Apertura;
        axes(handles.Brazo); %Carga la imagen en background   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,112.5,30);
        axes(handles.Brazo1); %Carga la imagen    
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,180,90);
        axes(handles.Brazo2); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,90,0);
        axes(handles.Brazo3); %Carga la imagen   
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        pintar(T1,T2,T3,T4,T5,op,x,y,z,0,0);
        handles.output = hObject;
        guidata(hObject, handles);
        Stop(puerto);
        
    % --- Executes on button press in Retorno.
    function Retorno_Callback(hObject, eventdata, handles)
        fclose(handles.Archivo);
        clear all; 
        close all;
        clc; 
        GMenu;


    % --- Executes on button press in Salvar.
    function Salvar_Callback(hObject, eventdata, handles)
        ang1=handles.Base;
        ang2=handles.Hombro;
        ang3=handles.Codo;
        ang4=handles.Pitch;
        ang5=handles.Roll;
        puerto=handles.Puerto;
        op=handles.Apertura;

        [d1,A1,A2,A3,A4,A5]=DirectoG(ang1,ang2,ang3,ang4,ang5,op,0,puerto,handles.BaseAnt,handles.HombroAnt,handles.CodoAnt,handles.PitchAnt,handles.RollAnt,handles.AperturaAnt);
            T5=A1*A2*A3*A4*A5;
            T4=A1*A2*A3*A4;
            T3=A1*A2*A3;
            T2=A1*A2;
            T1=A1;

        for i=1:3,
            for j=1:4,
                fprintf(handles.Archivo,'%6.4f %t',T5(i,j));
            end
            fprintf(handles.Archivo,'\n');
        end
        
        fprintf(handles.Archivo,'\n');
        fprintf(handles.Archivo,'\n');
        handles.output = hObject;
        guidata(hObject, handles);
        

    function OpenFile_Callback(hObject, eventdata, handles)


    function CloseFile_Callback(hObject, eventdata, handles)



    function DeleteFile_Callback(hObject, eventdata, handles)
   
        
        
        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Fin Push Buttons%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%Funciones extras%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function y=pintar(T1,T2,T3,T4,T5,op,x,y,z,vera,verb)

    %     DibBase;
    %     Hombro(T1);
    %     CyM(T2);
    %     CyM(T3);
    %     Gripper(T5,op);
    %     plot3(x,y,z),
    %     grid on
    %     view([112.5,30])  

    axis([-700 700 -700 700 -1 700])
    xlabel('Eje X');
    ylabel('Eje Y');
    zlabel('Eje Z');
    hold;
    % define la plano base
    a=150;
    b=350;
    c=0;
    x0=[ a -a -a  a];
    y0=[ b  b -b -b];
    z0=[ c  c  c  c];
    w0=[ 1  1  1  1];
    fill3(x0,y0,z0,'k');
    % define circunferencia de la base
    ndiv=40;
    radio1=90.90;
    radio2=86.26;
    offset=193;
    x1=radio1*cos(0:(2*pi/ndiv):2*pi);
    y1=radio1*sin(0:(2*pi/ndiv):2*pi);
    z1=radio1*zeros(ndiv+1,1)';
    x2=radio2*cos(0:(2*pi/ndiv):2*pi);
    y2=radio2*sin(0:(2*pi/ndiv):2*pi);
    z2=offset*ones(ndiv+1,1)';
    for i=1:ndiv,
        fill3([x1(i) x2(i) x2(i+1) x1(i+1)],[y1(i) y2(i) y2(i+1) y1(i+1)],[z1(i) z2(i) z2(i+1) z1(i+1)],'c');
    end  

    T=T1;
    a=101.0;
    b=340-193;
    c=102.0;
    % dibuja base
    w(1,:)=[ a -a -a  a]; % datos para x
    w(2,:)=[ b  b  b  b]; % datos para y
    w(3,:)=[ c  c -c -c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    % dibuja tapa izquierda
    a=101.0;
    b=340-193;
    c=102.0;
    d=55;
    e=162;
    % dibuja lado izquierdo
    wl(1,:)=[ a  a   d   -a   -a ]; % datos para x
    wl(2,:)=[ b  b-d b-e  b-e  b ]; % datos para y
    wl(3,:)=[ c  c   c    c    c ]; % datos para z
    wl(4,:)=[ 1  1   1    1    1 ]; % 
    w2=T*wl;
    fill3(w2(1,1:5),w2(2,1:5),w2(3,1:5),'y');
    % dibuja lado derecho
    wl(1,:)=[  a  a   d   -a   -a ]; % datos para x
    wl(2,:)=[  b  b-d b-e  b-e  b ]; % datos para y
    wl(3,:)=[ -c -c  -c   -c   -c ]; % datos para z
    wl(4,:)=[  1  1   1    1    1 ]; % 
    w3=T*wl;
    fill3(w3(1,1:5),w3(2,1:5),w3(3,1:5),'y');

    T=T2;
    % define parametros del codo
    a=220; % largo del segmento
    b=35;  % ancho
    c=95; % desface del segmento
    % dibuja segmento 
    w(1,:)=[ -a  0  0 -a]; % datos para x
    w(2,:)=[ -b -b  b  b]; % datos para y
    w(3,:)=[ -c -c -c -c]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    w(1,:)=[-a  0  0 -a]; % datos para x
    w(2,:)=[-b -b  b  b]; % datos para y
    w(3,:)=[ c  c  c  c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'y');
    
    T=T3;
    % define parametros del codo
    a=220; % largo del segmento
    b=35;  % ancho
    c=95; % desface del segmento
    % dibuja segmento 
    w(1,:)=[ -a  0  0 -a]; % datos para x
    w(2,:)=[ -b -b  b  b]; % datos para y
    w(3,:)=[ -c -c -c -c]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'y');
    w(1,:)=[-a  0  0 -a]; % datos para x
    w(2,:)=[-b -b  b  b]; % datos para y
    w(3,:)=[ c  c  c  c]; % datos para z
    w(4,:)=[ 1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'y');
    
    T=T5;
    o=op;

    % define parametros del codo
    a=151;   % largo del segmento
    b=75.5;  % comienzo base gripper
    c=20.0;  % ancho de la base gripper
    d=15.0;	% ancho del gripper
    
    % dibuja segmento fondo
    w(1,:)=[  c -c -c  c]; % datos para x
    w(2,:)=[ -c -c  c  c]; % datos para y
    w(3,:)=[ -a -a -a -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w1=T*w;
    fill3(w1(1,1:4),w1(2,1:4),w1(3,1:4),'g');
    
    % dibuja segmento origen del gripper
    w(1,:)=[ -c   -c     c     c  ]; % datos para x
    w(2,:)=[  c   -c    -c     c  ]; % datos para y
    w(3,:)=[ -a+b -a+b  -a+b  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w2=T*w;
    fill3(w2(1,1:4),w2(2,1:4),w2(3,1:4),'g');
    % dibuja segmento tapa superior
    w(1,:)=[ -c -c  c  c]; % datos para x
    w(2,:)=[  c  c  c  c]; % datos para y
    w(3,:)=[ -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w3=T*w;
    fill3(w3(1,1:4),w3(2,1:4),w3(3,1:4),'g');
    % dibuja segmento tapa inferior
    w(1,:)=[ -c -c  c  c]; % datos para x
    w(2,:)=[ -c -c -c -c]; % datos para y
    w(3,:)=[  -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w4=T*w;
    fill3(w4(1,1:4),w4(2,1:4),w4(3,1:4),'g');
    % dibuja segmento tapa lateral izquierda
    w(1,:)=[  c c  c c]; % datos para x
    w(2,:)=[  -c  -c  c c]; % datos para y
    w(3,:)=[ -a  -a+b -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w5=T*w;
    fill3(w5(1,1:4),w5(2,1:4),w5(3,1:4),'g');
    % dibuja segmento tapa lateral derecha
    w(1,:)=[  -c  -c  -c  -c]; % datos para x
    w(2,:)=[ -c  -c c c]; % datos para y
    w(3,:)=[  -a  -a+b  -a+b  -a]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w5=T*w;
    fill3(w5(1,1:4),w5(2,1:4),w5(3,1:4),'g');
    
    % dibuja plano del fondo del gripper
    w(1,:)=[ -o -o  o  o]; % datos para x
    w(2,:)=[  d -d -d  d]; % datos para y
    w(3,:)=[ -a+b  -a+b  -a+b  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w6=T*w;
    fill3(w6(1,1:4),w6(2,1:4),w6(3,1:4),'g');

    % dibuja plano izquierdo del gripper
    w(1,:)=[ -o -o -o -o]; % datos para x
    w(2,:)=[  d d -d -d]; % datos para y
    w(3,:)=[  -a+b  0  0  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w7=T*w;
    fill3(w7(1,1:4),w7(2,1:4),w7(3,1:4),'g');
    % dibuja plano derecho del gripper
    w(1,:)=[  o  o  o  o]; % datos para x
    w(2,:)=[  d d -d -d]; % datos para y
    w(3,:)=[  -a+b  0  0  -a+b]; % datos para z
    w(4,:)=[  1  1  1  1]; % 
    w8=T*w;
    fill3(w8(1,1:4),w8(2,1:4),w8(3,1:4),'g');
    
    plot3(x,y,z),
    grid on
    view([vera,verb])
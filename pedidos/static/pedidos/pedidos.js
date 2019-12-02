    
  
    // 
    
    $(document).ready(function() {
       
       var id_temp = ''
       var id_prov = ''
       var id_cat = ''
       var id_pag = ''
       var id_art = 0
       var continuar_procesando =0

       var total_articulos_pedidos = 0

       var seleccionados_como_encontrados = 0
       var is_staff='False'
       var usr_id = 0
       var usr_derecho // Variable utilizada para guardar el derecho
                       // del empleado a hacer alguna accion,
                       // ejemplo, crear pedidos (derecho 5)
                       // se actualizara en cada llamado segun la operacion
                       // se envia en la funcion que checa si existe empleado y si tiene derechos

       var tiene_derecho = 0  // Esta variable se usa conjuntamente
                              // con con la FUNCION A (checa por existencia de empleado) 
       var num_usr_valido = 0 // Variable para probar si el usuario es valido

       // deshabilita el boton procesar ventas al inicio de jquery
       $("#procesar_ventas").prop('disabled', true);


        // deshabilita botones de creacion de documentos

       $("#id_doc_temporada").prop('disabled', true);
       $("#id_doc_anio").prop('disabled', true);
       $("#id_doc_proveedor").prop('disabled', true);


      $('#busca_socio_javascr tbody').on('click', function() {
      var $row = $(this).closest('tr');  
      var x = $(".campo").eq(1).text();
      var y = $(".campo").eq(0).text();
      $('#id_pagina').val(x);
      $('#id_estilo').val(y);
      alert(x);
      alert(y);
      });

      $('#myCarouselCustom').carousel();

// Go to the previous item
$("#prevBtn").click(function(){
    $("#myCarouselCustom").carousel("prev");
});
// Go to the previous item
$("#nextBtn").click(function(){
    $("#myCarouselCustom").carousel("next");
});

      

  


       // LA SIGUIENTE FUNCION VALIDA QUE EL CAMPO
       // "ANTICIPO" SIEMPRE RECIBA UN VALOR NUMERIO


       $("#anticipo_id").keypress(function (e) {
     //if the letter is not digit then display error and don't type anything
            if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
        //display error message
                  //$("#errmsg").html("Solo numeros").show().fadeOut("slow");
                   alert("Ingrese solo numeros por favor..");
                   return false;
              }
         });
         //});

         // LA SIGUIENTE FUNCION VALIDA QUE EL CAMPO
       // "usuario id (password)" SIEMPRE RECIBA UN VALOR NUMERICO


       $("#usr_id").keypress(function (e) {
     //if the letter is not digit then display error and don't type anything
            if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
        //display error message
                  //$("#errmsg").html("Solo numeros").show().fadeOut("slow");
                   alert("El password es un código numérico, ingrese solo números por favor..");
                   return false;
              }
         });
         //});


       // F U N I C I O N   A  

      // FUNCION PARA VALIDAR QUE EXISTE EMPLEADO Y QUE TENGA DERECHOS 
      // AL MOMENTO DE HACER UN PEDIDO
      $("#usr_id").blur(function() {

                var usr_id = $(this).val()
                $("#procesar").prop('disabled',true)

            
                $.ajax({
                  url: '/pedidos/valida_usr/',
                  type: 'GET',
                  data:{'usr_id':usr_id,'usr_derecho':5},
                  success: function(data){
                            if (data.num_usr_valido == 0){
                                         
                              alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                              
                              $("#procesar").prop('disabled',true)
                            }

                            else{

                              num_usr_valido = data.num_usr_valido 

                              $("#procesar").prop('disabled',false)

                              if(data.tiene_derecho == 0){
                                        
                                      alert("Ud no tiene derechos como empleado para hacer pedidos !")

                                        $("#procesar").prop('disabled',true)

                              }
                              else {
                                        tiene_derecho = 1
                              };


                            }
                    
                    ;
                    
                    console.log(data.num_usr_valido);
                    console.log(data.tiene_derecho);

                   
                  },
                  error: console.log("algo pasa con data")
                });







            });

       // F U N I C I O N   B 

      // FUNCION PARA VALIDAR QUE EXISTE EMPLEADO Y QUE TENGA DERECHOS 
      // AL MOMENTO DE HACER PROCESAR COLOCACIONES
      $("#usr_id_colocaciones").blur(function() {

                var usr_id = $(this).val()
                $("#procesar_colocaciones").prop('disabled',true)

            
                $.ajax({
                  url: '/pedidos/valida_usr/',
                  type: 'GET',
                  data:{'usr_id':usr_id,'usr_derecho':11},
                  success: function(data){
                            if (data.num_usr_valido == 0){
                                         
                              alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                              
                              $("#procesar_colocaciones").prop('disabled',true)
                            }

                            else{

                              num_usr_valido = data.num_usr_valido 

                              $("#procesar_colocaciones").prop('disabled',false)

                              if(data.tiene_derecho == 0){
                                        
                                      alert("Ud no tiene derechos como empleado para procesar colocaciones !")

                                        $("#procesar_colocaciones").prop('disabled',true)

                              }
                              else {
                                        tiene_derecho = 1
                              };


                            }
                    
                    ;
                    
                    console.log(data.num_usr_valido);
                    console.log(data.tiene_derecho);

                   
                  },
                  error: console.log("algo pasa con data")
                });

                





            });

// F U N I C I O N   C 

      // FUNCION PARA VALIDAR QUE EXISTE EMPLEADO Y QUE TENGA DERECHOS 
      // AL MOMENTO DE CERRAR PEDIDO EN COLOCACIONES
      $("#usr_id_colocadosacerrar").blur(function() {

                var usr_id = $(this).val()
                $("#procesar_cierre_pedido").prop('disabled',true)

            
                $.ajax({
                  url: '/pedidos/valida_usr/',
                  type: 'GET',
                  data:{'usr_id':usr_id,'usr_derecho':11},
                  success: function(data){
                            if (data.num_usr_valido == 0){
                                         
                              alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                              
                              $("#procesar_cierre_pedido").prop('disabled',true)
                            }

                            else{

                              num_usr_valido = data.num_usr_valido 

                              $("#procesar_cierre_pedido").prop('disabled',false)

                              if(data.tiene_derecho == 0){
                                        
                                      alert("Ud no tiene derechos como empleado para cerrar pedidos !")

                                        $("#procesar_cierre_pedido").prop('disabled',true)

                              }
                              else {
                                        tiene_derecho = 1
                              };


                            }
                    
                    ;
                    
                    console.log(data.num_usr_valido);
                    console.log(data.tiene_derecho);

                   
                  },
                  error: console.log("algo pasa con data")
                });

                





            });


// F U N I C I O N   D 

      // FUNCION PARA VALIDAR QUE EXISTE EMPLEADO Y QUE TENGA DERECHOS 
      // AL MOMENTO DE RECEPCIONAR PEDIDOS

$("#procesar_recepcion").prop('disabled',true)



      $("#usr_id_pedidos_recepcionar").blur(function() {

                var usr_id = $(this).val()
                $("#procesar_recepcion").prop('disabled',true)

            
                $.ajax({
                  url: '/pedidos/valida_usr/',
                  type: 'GET',
                  data:{'usr_id':usr_id,'usr_derecho':12},
                  success: function(data){
                            if (data.num_usr_valido == 0){
                                         
                              alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                              
                              $("#procesar_recepcion").prop('disabled',true)
                            }

                            else{

                              num_usr_valido = data.num_usr_valido 

                              $("#procesar_recepcion").prop('disabled',false)

                              if(data.tiene_derecho == 0){
                                        
                                      alert("Ud no tiene derechos como empleado para recepcionar pedidos !")

                                        $("#procesar_recepcion").prop('disabled',true)

                              }
                              else {
                                        tiene_derecho = 1
                              };


                            }
                    
                    ;
                    
                    console.log(data.num_usr_valido);
                    console.log(data.tiene_derecho);

                   
                  },
                  error: console.log("algo pasa con data")
                });

                





            });

// F U N I C I O N   E



      // FUNCION PARA VALIDAR QUE EXISTE EMPLEADO Y QUE TENGA DERECHOS 
      // AL MOMENTO DE REGISTRAR UNA DEVOLUCION DE SOCIO

$("#procesar_devolucion_socio").prop('disabled',true)



      $("#usr_id_pedidos_recepcionar").blur(function() {

                var usr_id = $(this).val()
                $("#procesar_devolucion_socio").prop('disabled',true)

            
                $.ajax({
                  url: '/pedidos/valida_usr/',
                  type: 'GET',
                  data:{'usr_id':usr_id,'usr_derecho':12},
                  success: function(data){
                            if (data.num_usr_valido == 0){
                                         
                              alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                              
                              $("#procesar_devolucion_socio").prop('disabled',true)
                            }

                            else{

                              num_usr_valido = data.num_usr_valido 

                              $("#procesar_devolucion_socio").prop('disabled',false)

                              if(data.tiene_derecho == 0){
                                        
                                      alert("Ud no tiene derechos como empleado para recepcionar pedidos !")

                                        $("#procesar_devolucion_socio").prop('disabled',true)

                              }
                              else {
                                        tiene_derecho = 1
                              };


                            }
                    
                    ;
                    
                    console.log(data.num_usr_valido);
                    console.log(data.tiene_derecho);

                   
                  },
                  error: console.log("algo pasa con data")
                });

                





            });






          





       $('#listapedidosgeneral').DataTable( {
        autoFill: true
          });

       $('#lista_documentos').DataTable( {
        autoFill: true
          });

       //$('#colocaciones_detalle_tabla').DataTable( {
        
       //   autoFill: true

       //   });


       // FIJA UN CUADRO CON TOTALES EN LA VENTA
       // Codigo Jquery que permite congelar una parte
       // de la pantalla de ventas ( la que muestra totales)
       // trabaja en conjunto con la seccion 'style css' definida
       // en el archivo "base.html"
       // En la plantilla "despliega_venta.html" se le asigna al div
       // el idenficador "cuadro-fijo"

    
       // check where the cuadro-fijo-div is  
    var offset = $('#cuadro-fijo').offset();  
    $(window).scroll(function () {    
        var scrollTop = $(window).scrollTop(); 
        // check the visible top of the browser     
        if (offset.top<scrollTop) {
            $('#cuadro-fijo').addClass('fixed'); 
        } else {
            $('#cuadro-fijo').removeClass('fixed');   
        }
    }); 



    //using jQuery for getCookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');


       



      //$("#listapedidosgeneral").dataTable();

      $("#imp_prueba").click(function(){

        window.print();


      });

      
       
       $("#procesar").prop('disabled', true);
       $("#sucursal").prop('disabled', true);
       $("#idpedido").prop('disabled',true);
       $("#procesar_colocaciones").prop('disabled',true);
       $("#procesar_cierre_pedido").prop('disabled',true);
       $("#id_nueva_fecha_llegada ").prop('disabled',true)
      // $('#btn_trae_colocaciones').prop('disabled',true);


       //bloquea campos de tipo de servicio, via de solicitud y anticipo
       // para el caso de los socios que no son staff
       console.log("variable staff aqui :");
       console.log(is_staff);
       if (is_staff == 'False'){
        $("#viasolicitud_id").prop('disabled',true);
        $('#tiposervicio_id').prop('disabled',true);
        $('#anticipo_id').prop('disabled',true);
        $('#usr_id').prop('disabled',true);
       }




       //alert("jquery funciona !")

        // La funcion es para ver que funciona JavaScript y va amarrada al tag
        // msgid que esta en el template "index", para probar hay que descomentar aqui y en 
        // el template index.

       //$("#msgid").html("This is Hello World by JQuery");


       /* Exampleo of Use jQuery to read the text values in an HTML table

       $('#coloc_detail_table tr').each(function(row, tr){
            TableData = TableData 
                + $(tr).find('td:eq(0)').text() + ' '  // Pedido (no visible en tabla)
                + $(tr).find('td:eq(1)').text() + ' '  // producto (No visible en tabla)
                + $(tr).find('td:eq(2)').text() + ' '  // catalogo (no visible en tabla)
                + $(tr).find('td:eq(3)').text() + ' '  // nolinea (no visible en tabla)
                + $(tr).find('td:eq(14)').val() + ' '  // encontrado (visible en tabla)
                + '\n';
        });

        // Store HTML Table Values into Multidimensional Javascript Array Object 

        var TableData = new Array();
            
        $('#sampleTbl tr').each(function(row, tr){
            TableData[row]={
                "taskNo" : $(tr).find('td:eq(0)').text()
                , "date" :$(tr).find('td:eq(1)').text()
                , "description" : $(tr).find('td:eq(2)').text()
                , "task" : $(tr).find('td:eq(3)').text()
            }
        }); 
        TableData.shift();  // first row is the table header - so remove

      



        */


      $('#id_marcartodo_nollego').change(function(){ 

        if ($('#id_marcartodo_nollego').prop('checked')) {
                  
                   $("#id_nueva_fecha_llegada").prop('disabled',false);


        }
        else {

          $("#id_nueva_fecha_llegada").val('');
          $("#id_nueva_fecha_llegada").prop('disabled',true);


        }

      });



      /*$('#productos_por_vender tr').on('click', function(){
             var dato = $(this).find('td:first').html();
              $('#txtNombre').val(dato);
              });*/




      // RUTINA PARA CUANDO SE SELECCIONA EL CAMPO 'DESCUENTO' EN LA VENTA
      // VA I CALCULA EL FACTOR DE DESCUENTO Y SE LO APLICA AL PRECIO.
      /*  
      $('.checkbox_dscto').change(function(){ 
            

        if ($(this).prop('checked')) {
           
            //$("#art_elegidos").html(function(i, val) { return val*1+1 });
           
            id_prov = $(this).parents('tr').find('td:eq(14)').text();
            precio = $(this).parents('tr').find('td:eq(12)').text();
            var $this_var = $(this)
            

            $.ajax({
                  url: '/pedidos/calcula_descuento/',
                  type: 'GET',
                  data:{'id_prov':id_prov,'id_socio':id_socio},
                  success: function(data){
                    
                    
                    console.log(data);
                    
                    console.log(data.factor_descuento);

                    var dscto = precio*data.factor_descuento;
                    var nvo_precio = precio - dscto
                    //nvo_precio = Math.round(parseInt(nvo_precio))

                    
                    $this_var.parents('tr').find('td:eq(12)').text(nvo_precio.toFixed(2)); // .
                    
                    console.log("tr:")
                    console.log($this_var.parents('tr').find('td:eq(12)').text())
                                       
                  },

                  error: console.log("algo pasa con data")
                });

        
        }
      else {

        var precio_normal = $(this).parents('tr').find('td:eq(15)').text();
        console.log('precio normal:')
        console.log(precio_normal)
        $(this).parents('tr').find('td:eq(12)').text(precio_normal);

      }  
        
      }); */



      // ********************************************
      // Logica para cuando cambia el combo proveedor_rpte_cotejo
      //*********************************************


      $('#id_proveedor_rpte_cotejo').change(function(){ //1
      

        // Comienza por inicializar elementos subseuentes
        // con cero o blancos
        //alert($('#id_proveedor').val())
        
        //vacia el combo catalogo preparandolo a recibir nuevos valores.
        id_prov = $('#id_proveedor_rpte_cotejo').val();
        console.log('proveedor:');
        console.log(id_prov);

        // esta asignacion la hace para inicialice almacenes en la rutina de colocaciones
        //$('#id_cierre_rpte_cotejo').val(''); 
        console.log("antes de ajax");
        $.ajax({ //2
          url: '/pedidos/combo_proveedor_rpte_cotejo/',
          type: 'GET',
          data:{'id_prov':id_prov,},

          success: function(data){ //3

                            var tableData = '';

                            $('tbody').empty(); // Borra tabla

                            if (data.length==0){
                                alert("No se encontraron coincidencias !")
                            };
                            tableData += "<tr><th>id</th><th>Pedido Num</th><th>Referencia</th><th>Fecha Cierre</th><th>Hora Cierre</th><th>Fecha llegada</th><th>Tot. Articulos</th><th>Importe</th><th>Almacen</th></tr>"; // Dibuja encab
                            //Ajax nos retorna en data un arreglo de arreglos..asi
                            // que primeramente "each(data....)" hace referecia a 
                            // cada arreglo dentro del arreglo y "value" nos trae
                            // el conenido de cada arreglo, asi que tenemos que hacer
                            // referencia a value[0], value[1]... etc para poder traer los campos que nos interesan.

                            $('tbody').append( //4
                                $.each(data, function(key,value){ //5
                                    //<td><a href="/pedidos/pedidosgeneraldetalle/{{ item.pedido }}/{{item.productono}}/{{item.catalogo}}/{{item.nolinea}}"> {{ item.idestilo }} </a></td>                                   
                                    tableData += '<tr>';
                                    tableData += '<td>'+'<a href="/pedidos/modifica_cierre/'+value['id']+'">'+value['id']+'</a></td>'; // link id para modificar.
                                     tableData += '<td>' +value['NumPedido']+'</td>';
                                     tableData += '<td>' + value['referencia'] + '</td>';
                                     tableData += '<td>' + value['FechaCierre'] + '</td>';
                                     tableData += '<td>' + value['HoraCierre'] + '</td>'; 
                                     tableData += '<td>' + value['FechaColocacion'] + '</td>'; // Esta fecha de colocacion es en realidad la fecha tentativa de llagada del pedido
                                     tableData += '<td>' + value['total_articulos'] + '</td>';
                                     tableData += '<td>' + value['importe'] + '</td>';
                                     tableData += '<td>' + value['RazonSocial'] + '</td>';
                                                                
                                     
                                     
                                    tableData += '</tr>';
                                    
                                }) //5
                            ), //4
                            $('#tot').text("Total de registros encontrados: "+data.length);
                            $('tbody').html(tableData);      

                    }, //3

            
          

          error: function(data){ //6
            console.log("error en recepcion de datos de cierres");
          }//6

        }); //2
      })//1










        // ACTUALIZA CONTADOR DE REGISTROS SELECCIONADOS PARA CERRAR PEDIDO



         $('.checkbox_elegido').click(function() {
            // alert( "Handler for .click() called." );
            if ($(this).prop('checked')){ // Dado que la clase checkbox_elegido se asocia a puros checkbox, solamente se revisa por su propiedad checked.
             $("#art_elegidos").html(function(i, val) { return val*1+1 });
           }

            else {
            
              $("#art_elegidos").html(function(i, val) { return val*1-1 });


                }
          });



// ACTUALIZA CONTADOR DE REGISTROS SELECCIONADOS PARA VENTAS



         $('.checkbox_aplicar_venta').click(function() {
             // alert( "Handler for .click() called." );



            var precio = $(this).parents('tr').find('td:eq(12)').text();
            var precio_normal = $(this).parents('tr').find('td:eq(15)').text();

            precio = Math.round(precio)
            precio_normal = Math.round(precio_normal)



            // deshabilita el checkbox de descuento una vez que se selecciono el articulo.
            // Obsrevar que se tiene not(this) para que no deshabilite tambien el checkbox_aplicar_venta
            $(this).parents('tr').find('input[type=checkbox]').not(this).attr('disabled',true)

            

            if ($(this).prop('checked')){ // Dado que la clase checkbox_elegido se asocia a puros checkbox, solamente se revisa por su propiedad checked.
                

                
             $("#art_elegidos").html(function(i, val) { return val*1+1 });


             // Incrementa el monto de lo vendido

             $("#totalventas").html(function(i, val) { return val*1 + parseInt(precio_normal) });
             $("#totaldsctos").html(function(i, val) { return val*1 + (parseInt(precio_normal)- parseInt(precio)) });
             $("#totalgral").html(function(i, val) { return val*1 + parseInt(precio_normal) - (parseInt(precio_normal) - parseInt(precio)) });


             if( $("#totalgral").html()<0){
                $("#totalgral").val(0);
             }

                         
          }

            else {

              // Se habilita el checkbox descuento

              $(this).parents('tr').find('input[type=checkbox]').not(this).attr('disabled',false)
            
              $("#art_elegidos").html(function(i, val) { return val*1-1 });

              $("#totalventas").html(function(i, val) { return val*1 - parseInt(precio_normal) });
              $("#totaldsctos").html(function(i, val) { return val*1 - (parseInt(precio_normal) - parseInt(precio)) });
              $("#totalgral").html(function(i, val) { return val*1 - parseInt(precio_normal) + (parseInt(precio_normal) - parseInt(precio)) });

                if( $("#totalgral").html()< 0){
                      $("#totalgral").val(0);
                  }

                }

              if($("#totalventas").html()>0){

                      $("#procesar_ventas").prop('disabled', false);
                 } else {
                      $("#procesar_ventas").prop('disabled', true);
               }






          });







// ACTUALIZA CONTADOR DE REGISTROS SELECCIONADOS PARA CREDITOS



         $('.checkbox_aplicar_credito').click(function() {
             // alert( "Handler for .click() called." );



             

            var monto = parseInt($(this).parents('tr').find('td:eq(3)').text(),10);

            console.log("el monto es:")
            console.log(monto)

            console.log("totalgral:")
            console.log($('#totalgral').text())
            console.log($('#totalgral').val())

            if ($(this).prop('checked')){ // Dado que la clase checkbox_elegido se asocia a puros checkbox, solamente se revisa por su propiedad checked.
            
                // Incrementa el monto de creditos y decremente el total de general

                $("#totalcreditos").html(function(i, val) { return val*1 + (parseInt(monto)) });
                $("#totalgral").html(function(i, val) { return val*1 - parseInt(monto) });
                if( $("#totalgral").html()< 0){
                    $("#totalgral").val(0);
                  }
                //if( monto > parseInt($("#totalgral").text(),10)) {

                //      alert("El credito es mayor al total de la transaccion, no puede ser aplicado !");
                //      $(this).prop('checked',false)

                //}
                //else {
                      // Incrementa el monto de creditos y decremente el total de general

                  //    $("#totalcreditos").html(function(i, val) { return val*1 + (parseInt(monto)) });
                  //    $("#totalgral").html(function(i, val) { return val*1 - parseInt(monto) });
                  //}

          }

            else {

              // Decrementa total de creditos e incrementa total gral

            

              $("#totalcreditos").html(function(i, val) { return val*1 - parseInt(monto) });
              $("#totalgral").html(function(i, val) { return val*1 + parseInt(monto) });


              if( $("#totalgral").html()< 0){
                $("#totalgral").val(0);
              }



                }
          });



// ACTUALIZA CONTADOR DE REGISTROS SELECCIONADOS PARA CARGOS



         $('.checkbox_aplicar_cargo').click(function() {
             // alert( "Handler for .click() called." );

            var monto = $(this).parents('tr').find('td:eq(3)').text();

        

            if ($(this).prop('checked')){ // Dado que la clase checkbox_elegido se asocia a puros checkbox, solamente se revisa por su propiedad checked.
            
              // Incrementa el monto de creditos y decremente el total de general

             $("#totalcargos").html(function(i, val) { return val*1 + (parseInt(monto)) });
             $("#totalgral").html(function(i, val) { return val*1 + parseInt(monto) });

             if( $("#totalgral").html()< 0){
                $("#totalgral").val(0);
             }



              /*
                if( monto > parseInt($("#totalgral").text(),10)) {

                      alert("El cargo es mayor al total de la transaccion, no puede ser aplicado !");
                      $(this).prop('checked',false)

                }
                else {



             // Incrementa el monto de creditos y decremente el total de general

             $("#totalcargos").html(function(i, val) { return val*1 + (parseInt(monto)) });
             $("#totalgral").html(function(i, val) { return val*1 + parseInt(monto) });

                  }*/
          }

            else {

              // Decrementa total de creditos e incrementa total gral

              $("#totalcargos").html(function(i, val) { return val*1 - parseInt(monto) });
              $("#totalgral").html(function(i, val) { return val*1 - parseInt(monto) });

              if( $("#totalgral").html()< 0){
                $("#totalgral").val(0);
              }


                }
          });












         // MANEJO DE TABLA EN PROCESAR_COLOCACIONES


        // Busca elemementos en tabla de colocaciones, los anexa a un 
        // arreglo Jquery de dos dimensiones
        // y finalmente convierte el objeto arreglo a formato json
        // es invocada dentro de la rutina de "procesar_colocaciones".

        

        function storeTblValues()
        {
            var TableData = new Array();

            $('#colocaciones_detalle_tabla tr').each(function(row, tr){
                TableData[row]={
                    "Pedido" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                    , "ProductoNo" :$(tr).find('td:eq(1)').text() // Agrega el producto ( no visible en tabla)
                    , "Catalogo" : $(tr).find('td:eq(2)').text() // Agrega el catalogo ( no visible en tabla)
                    , "Nolinea" : $(tr).find('td:eq(3)').text() // Agrega el Nolinea (no visible en tabla)
                    , "ver_ant_encontrado" : $(tr).find('td:eq(4)').text()
                    , "status" : $(tr).find('td:eq(5)').text()
                    , "encontrado": $(tr).find('td:eq(16)').find("select option:selected").attr('value') // Agrega "colocado", esta si es visible en tabla y se agrega el valor, no el texto
                    //, "notas": $(tr).find('td:eq(26)').find('input').value()
                    // Agrega "colocado", esta si es visible en tabla y se agrega el valor, no el texto
                    , "notas": $(tr).find("td:eq(26) input[type='text']").val()
                }     
            }); 
            TableData.shift();  // first row will be empty - so remove
            return TableData;
        }


        // MANEJO DE TABLA EN PROCESAR CIERRE DE PEDIDOS

// La siguiente funcion es casi igual a la anterior y hace lo mismo solo que para los pedidos que se van a cerrar, es invocada 
// desde la rutina 'procesar_cierre_pedidos'
        function storeTblValues_1()
        {
            var TableData = new Array();

            $('#coloc_detail_table tr').each(function(row, tr){
                if ($(tr).find('td:eq(16)').find('input').prop('checked')){


                  TableData[row]={
                      "Pedido" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                      , "ProductoNo" :$(tr).find('td:eq(1)').text() // Agrega el producto ( no visible en tabla)
                      , "Catalogo" : $(tr).find('td:eq(2)').text() // Agrega el catalogo ( no visible en tabla)
                      , "Nolinea" : $(tr).find('td:eq(3)').text() // Agrega el Nolinea (no visible en tabla)
                      , "ver_ant_encontrado" : $(tr).find('td:eq(4)').text()
                      , "status" : $(tr).find('td:eq(5)').text()
                      , "elegido": $(tr).find('td:eq(16)').find('input').prop('checked') // Agrega "elegido", como es un checkbox usamos la funcion prop('checked') para traernos el va 
                  }
                }    
            }); 
            TableData.shift();  // first row will be empty - so remove
            return TableData;
        }

//      MANEJO DE TABLA PARA PROCESAR RECEPCION DE ARTICULOS

        function storeTblValues2()
        {
            var TableData = new Array();

            $('#coloc_detail_table tr').each(function(row, tr){
                TableData[row]={
                    "Pedido" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                    , "ProductoNo" :$(tr).find('td:eq(1)').text() // Agrega el producto ( no visible en tabla)
                    , "Catalogo" : $(tr).find('td:eq(2)').text() // Agrega el catalogo ( no visible en tabla)
                    , "Nolinea" : $(tr).find('td:eq(3)').text() // Agrega el Nolinea (no visible en tabla)
                    , "status" : $(tr).find('td:eq(4)').text()
                    , "incidencia": $(tr).find('td:eq(13)').find("select option:selected").attr('value') // Agrega "colocado", esta si es visible en tabla y se agrega el valor, no el texto
                }    
            }); 
            TableData.shift();  // first row will be empty - so remove
            return TableData;
        }

        // MANEJO DE TABLA EN PROCESAR LOS REGISTROS DE VENTA

// La siguiente funcion es casi igual a la anterior y hace lo mismo solo que para los pedidos que se van a cerrar, es invocada 
// desde la rutina 'procesar_cierre_pedidos'
        function storeTblValues_ventas()
        {
            var TableData_ventas = new Array();

            $('#productos_por_vender tr').each(function(row, tr){
                if ($(tr).find('td:eq(13)').find('input').prop('checked')){


                  TableData_ventas[row]={
                      "Pedido" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                      , "ProductoNo" :$(tr).find('td:eq(1)').text() // Agrega el producto ( no visible en tabla)
                      , "Catalogo" : $(tr).find('td:eq(2)').text() // Agrega el catalogo ( no visible en tabla)
                      , "Nolinea" : $(tr).find('td:eq(3)').text() // Agrega el Nolinea (no visible en tabla)
                      , "status": $(tr).find('td:eq(4)').text() // 
                      , "precio" : $(tr).find('td:eq(12)').text()
                      , "vta_elegida": $(tr).find('td:eq(13)').find('input').prop('checked') // Agrega "elegido", como es un checkbox usamos la funcion prop('checked') para traernos el va 
                  }
                }    
            }); 
            TableData_ventas.shift();  // first row will be empty - so remove
            return TableData_ventas;
        }

        // MANEJO DE TABLA EN PROCESAR LOS REGISTROS DE CREDITOS ( EN VENTAS)

// La siguiente funcion es casi igual a la anterior y hace lo mismo solo que para los pedidos que se van a cerrar, es invocada 
// desde la rutina 'procesar_cierre_pedidos'
        function storeTblValues_creditos()
        {
            var TableData_creditos = new Array();

            $('#creditos_vta tr').each(function(row, tr){
                if ($(tr).find('td:eq(4)').find('input').prop('checked')){


                  TableData_creditos[row]={
                      "no_docto_credito" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                      , "monto_credito" :$(tr).find('td:eq(3)').text() // Agrega el producto ( no visible en tabla)
                      , "credito_elegido": $(tr).find('td:eq(4)').find('input').prop('checked') // Agrega "elegido", como es un checkbox usamos la funcion prop('checked') para traernos el va 
                  }
                }    
            }); 
            TableData_creditos.shift();  // first row will be empty - so remove
            return TableData_creditos;
        }

        // MANEJO DE TABLA EN PROCESAR REGISTROS DE CARGOS (EN VENTAS)

// La siguiente funcion es casi igual a la anterior y hace lo mismo solo que para los pedidos que se van a cerrar, es invocada 
// desde la rutina 'procesar_cierre_pedidos'
        function storeTblValues_cargos()
        {
            var TableData_cargos = new Array();

            $('#cargos_vta tr').each(function(row, tr){
                if ($(tr).find('td:eq(4)').find('input').prop('checked')){


                  TableData_cargos[row]={
                      "no_docto_cargo" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                      , "monto_cargo" :$(tr).find('td:eq(3)').text() // Agrega el producto ( no visible en tabla)
                      , "cargo_elegido": $(tr).find('td:eq(4)').find('input').prop('checked') // Agrega "elegido", como es un checkbox usamos la funcion prop('checked') para traernos el va 
                  }
                }    
            }); 
            TableData_cargos.shift();  // first row will be empty - so remove
            return TableData_cargos;
        }


//      MANEJO DE TABLA PARA DEVOLUCION DE SOCIO

        function storeTblValues_dev_socio()
        {
            var TableData = new Array();

            $('#coloc_detail_table tr').each(function(row, tr){
                TableData[row]={
                    "Pedido" : $(tr).find('td:eq(0)').text()  // Agrega el pedido ( columna no visible en tabla)
                    , "ProductoNo" :$(tr).find('td:eq(1)').text() // Agrega el producto ( no visible en tabla)
                    , "Catalogo" : $(tr).find('td:eq(2)').text() // Agrega el catalogo ( no visible en tabla)
                    , "Nolinea" : $(tr).find('td:eq(3)').text() // Agrega el Nolinea (no visible en tabla)
                    , "status" : $(tr).find('td:eq(4)').text()
                    , "incidencia": $(tr).find('td:eq(13)').find("select option:selected").attr('value') // Agrega "colocado", esta si es visible en tabla y se agrega el valor, no el texto
                }    
            }); 
            TableData.shift();  // first row will be empty - so remove
            return TableData;
        }    










       // funcion para activar el picker de fecha en consulta_pedidos
     $('.datepicker').datepicker({dateFormat: 'dd/mm/yy'});
      //$('.datepicker').datepicker();
      

      // Valida que exista socion en base de datos, si no existe regresa el foco al cursor de numero de socio.
      $('#id_socio').blur(function(){
        id_socio = $('#id_socio').val();
        console.log(id_socio) 
        $.ajax({
          url: '/pedidos/existe_socio/',
          type: 'POST',
          data:{'id_socio':id_socio},
          success: function(data){

            console.log('El dato que llega es:',data)

            // La validacion del numero de socio se llevara a cabo
            // siempre cuando el numero de pedido sea cero; si hay numero de pedido
            // la validacion de numero de socio sale sobrando.

            if (data == 'NO' && $("#id_numpedido").val() == '0')
               { alert("Error: Numero de socio no registrado !, busquelo por nombre");
                $("#id_socio").val(1);
                $("#id_socio").selectRange(0);

                }
          },
              
        });
                       

      });



      // TRAE NOMBRE DE SOCIO.
      $('#id_socionum').blur(function(){
        id_socio = $('#id_socionum').val();
        console.log(id_socio) 
        $.ajax({
          url: '/pedidos/trae_nombre_socio/',
          type: 'POST',
          data:{'id_socio':id_socio},
          success: function(data){

            console.log('El dato que llega es:',data)

            // La validacion del numero de socio se llevara a cabo
            // siempre cuando el numero de pedido sea cero; si hay numero de pedido
            // la validacion de numero de socio sale sobrando.

            $('#muestra_nombre_socio').text(data);

            
          },
              
        });
                       

      });



        

        $.fn.selectRange = function(start, end) {
                if(!end) end = start;
                return this.each(function() {
                    if (this.setSelectionRange) {
                       this.focus();
                       this.setSelectionRange(start, end);
                }   else if (this.createTextRange) {
                        var range = this.createTextRange();
                        range.collapse(true);
                        range.moveEnd('character', end);
                        range.moveStart('character', start);
                        range.select();
                  }
                });
        };


             

      
      // Funcion para inicializar combos

      function inicializa_combos(){

        $('id_proveedor').val(0);
        //$('#id_temporada').val('0');
        //$('#id_catalogo').val('SELECCIONE...'); 
        $('#id_pagina').val('0');
        $('#id_estilo').val('SELECCIONE...');
        $('#id_marca').val('SELECCIONE...');
        $('#id_color').val('SELECCIONE...');
        $('#id_talla').val('SELECCIONE...');
        $('#id_suc').val(0);
        $('#id_tallaalt').val('');
        //$('#id_fechamaximaentrega').val('01/01/1901');

        var d = new Date();

        var month = d.getMonth()+1;
        var day = d.getDate();

        //var output = d.getFullYear() + '/' +
        //    ((''+month).length<2 ? '0' : '') + month + '/' +
        //    ((''+day).length<2 ? '0' : '') + day;
        var output = ((''+day).length<2 ? '0' : '') + day + '/' + 
                     ((''+month).length<2 ? '0' : '') + month + '/' +
                     d.getFullYear();      


        $('#id_fechamaximaentrega').val(output);



      }

      function valida_fechamaximaentrega()
      {
        
        h = $('#id_fechamaximaentrega').val();
        l = $('#id_plazoentrega option:selected').text();
        //l = jQuery.trim(l);
        if ($('#id_fechamaximaentrega').val() == '01/01/1901' && $('#id_plazoentrega option:selected').text() == "Fecha")
          {
             return false;
          }
        else
         {
              return true;
          }
        
      
        
      };

       // ********************************************
      // Logica para cuando cambia combo de clase 'sel_encontrado'
      // para template de: colocaciones_detalle.html 
      //*********************************************
      var val_anterior = '' // Esta variable se usa en esta rutina y en la siguiente.

      $(".sel_encontrado").on('focus', function () {
        // Store the current value on focus and on change
        val_anterior = $(this).val();
      });




      $('.sel_encontrado').change(function(){
        // #coloc_detail_table id_encontrado select
        
       

        if ($(this).val() == 'S' ) { 

            seleccionados_como_encontrados += 1;
            $("#total_encontrados").html(function(i, val) { return val*1+1 });

            }

        else { 

                if ($(this).val() != 'S' && val_anterior == 'S')

                  {
                    // #coloc_detail_table id_encontrado select
                      seleccionados_como_encontrados -= 1;
                       $("#total_encontrados").html(function(i, val) { return val*1-1 });
                  }
                 
             };

        

      });



      // ********************************************
      // Logica para cuando cambia combo de clase 'sel_incidencia'
      // para template de: muestra_registros_recepcionar.html 
      //*********************************************
    

      $(".sel_incidencia").on('focus', function () {
        // Store the current value on focus and on change
        val_anterior = $(this).val(); // utiliza la variable definida en la rutina anterior.
      });




      $('.sel_incidencia').change(function(){
        // #coloc_detail_table id_encontrado select
        
       

        if ($(this).val() == '1' ) { 

            seleccionados_como_encontrados += 1;
            $("#total_recibidos").html(function(i, val) { return val*1+1 });

            }

        else { 

                if ($(this).val() != '1' && val_anterior == '1')

                  {
                    // #coloc_detail_table id_encontrado select
                      seleccionados_como_encontrados -= 1;
                       $("#total_recibidos").html(function(i, val) { return val*1-1 });
                  }
                 
             };

        

      });






      id_prov = $('#id_proveedor').val();
      console.log(id_prov); 
      id_temp = $('#id_temporal').val();
      console.log(id_temp); 
      id_cat = $('#id_catalogo').val();



      // ********************************************
      // Logica para cuando cambia el combo proveedor
      //*********************************************


      $('#id_proveedor').change(function(){
      

        // Comienza por inicializar elementos subseuentes
        // con cero o blancos
        //alert($('#id_proveedor').val())
        
        $('#id_catalogo').empty(); 
        $('#id_pagina').val('0');
        $('#id_estilo').empty();
        $('#id_marca').empty();
        $('#id_color').empty();
        $('#id_talla').empty();
        $('#id_temporada').val('0'); // vacia el combo catalogo preparandolo a recibir nuevos valores.
        id_prov = $('#id_proveedor').val();

        // esta asignacion la hace para inicialice almacenes en la rutina de colocaciones
        $('#id_almacen').val('0'); 
        console.log("antes de ajax");
        $.ajax({
          url: '/pedidos/combo_almacenes/',
          type: 'GET',
          data:{'id_prov':id_prov,},

          success: function(data){

            
            $('#id_almacen').empty(); // vacia el combo catalogo preparandolo a recibir nuevos valores.
             console.log(data);
            for (var i=4;i <= data.length;i+=2){
               
             // $('<option/>').val(data[i+1]).html(data[i+1]).appendTo('#id_almacen');
                 resto = i%2;
                 console.log("valor de i");
                 console.log(i);
                 console.log("resto:");
                 console.log(resto);
                 if( resto =! 0){
                   $('<option/>').val(data[i-1]).html(data[i]).appendTo('#id_almacen');
                   //$('<option/>').val(data[i+1]).appendTo('#id_almacen');
                   //$('<option/>').html(data[i]).appendTo('#id_almacen');
                 };

              }

            
          },
          error: console.log("error en recepcion de datos de almacenes"),

        });
      }); 


      
      // ******************************
      // Logica para cuando cambia combo temporada 
      //*******************************

      // observar que la funcion tiene el parametro 'e' ya que es utilizado en el llamado eventPrevent(e)..mas abajo.
      $('#id_temporada').change(function(e){
        
         //alert("funciona jquery");
        // Inicializa elementos subsecuentes para obligar a su captura.  
        $('#id_pagina').val('0');
        $('#id_estilo').empty();
        $('#id_marca').empty();
        $('#id_color').empty();
        $('#id_talla').empty();
        
        id_prov = $('#id_proveedor').val()
        id_temp = $('#id_temporada').val(); // inicializa la variebla temp con el valor que tenga.
        
        
        $.ajax({
          url: '/pedidos/combo_catalogos/',
          type: 'GET',
          data:{'id_prov':id_prov,'id_temp':id_temp},
          dataType:'json',
          success: function(data){

            var procesar = 1;
            console.log("valores de data:")
            console.log(data)
            $.each(data, function(index, value) {

                if (index == 'l'){
                     lista = value   }
                 
                else { if (index == 'adquirio_catalogo'){
                          compro_catalogo = value
                
                          }
                        else{
                          is_staff = value
                        }
                  };

            }); 
            console.log("valores de lista y compro catalogo:")
            console.log(lista)
            console.log(compro_catalogo)
            console.log(is_staff)
                
            if (compro_catalogo == 0 && !(is_staff) ){

                alert("Estimado socio, necesita primero adquirir este catalogo para poder ordenar productos !, le invitamos a pasar a cualquiera de nuestras sucursales para adquirirlo.");
                procesar = 0;
                
            }

            else {
              if ( compro_catalogo == 0 && is_staff  ){

                e.preventDefault();
                var answer=confirm('Este socio aun no adquiere este catalogo, desea continuar ? ');
                if ( ! answer ) {
                  
                  procesar = 0;
              

                }
                else{

                  procesar = 1;
                };
              }

            };

            if ( procesar == 1) {

              $('#id_catalogo').empty(); // vacia el combo catalogo preparandolo a recibir nuevos valores.
        
              for (var i=0;i<lista.length;i++){
                $('<option/>').val(lista[i]).html(lista[i]).appendTo('#id_catalogo');
              }
             
            }  
        
            

            
          },
          error: console.log("error en recepcion de datos de catalogos"),

        });
                              

      });


      
      


      // ********************************************
      // Logica para cuando cambia el combo catalogos
      //*********************************************
      
      $('#id_catalogo').change(function(){
      

        // Comienza por inicializar elementos subseuentes
        // con cero o blancos
         
        $('#id_pagina').val('0');
        $('#id_estilo').empty();
        $('#id_marca').empty();
        $('#id_color').empty();
        $('#id_talla').empty();
      });


      // ***********************************
      // Logica llenar el combo de estilos
      // ************************************ 

      $('#id_pagina').change(function(){
        //alert("cambio")
        
        // Si cambia la pagina llena con blancos elementos subsecuentes
        $('#id_marca').empty();
        $('#id_color').empty();
        $('#id_talla').empty();
        
        // Inicializa variables que se pasaran al servidor 
        // para la busqueda de los estilos
        
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $.trim($(this).val());

        
        
        $.ajax({
          
          url: '/pedidos/combo_estilos/',
          type: 'GET',
          data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag},
          success: function(data){
            $('#id_estilo').empty(); // vacia el estilo para que reciba nuevos valores
              if (data[0] != undefined ) { 
                for (var i=0;i<data.length;i++){
                  $('<option/>').val(data[i]).html(data[i]).appendTo('#id_estilo');
                };
            } else {
                alert("No se encontraron estilos con el numero de pagina que nos esta dando, intente con otro numero de pagina !");
                $("#id_pagina").val('0');
            };

            console.log(data);
          },
          error: function(){ 
            alert("Error en recepcion de datos de estilos");
          },

        });
                              

      });

      // ***********************************
      // Logica para llenar combo de marca
      // ************************************ 

      $('#id_estilo').change(function(){
        
        // Si cambia el estilo llena con blancos elementos subsecuentes
        $('#id_color').empty();
        $('#id_talla').empty();
        
        // Inicializa variables que se pasaran al servidor 
        // para la busqueda de las marcas
        
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $('#id_pagina').val();

        // ojo: En la siguiente linea la asignacion a la variable "id_est" debiera
        // funcionar con la sentencia id_est = $('this').val() dado que 
        // me encuentro dentro de #id_estilo,sin
        // embargo no funciono. arrojaba el error http 1.1 500
        // lo cambie a como sigue y funciono, checar.

        id_est = $('#id_estilo').val(); //  <-- ojo

        
        
        $.ajax({
          
          url: '/pedidos/combo_marcas/',
          type: 'GET',
          data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est},
          success: function(data){
            $('#id_marca').empty(); // vacia el estilo para que reciba nuevos valores
              if (data[0] != undefined ) { 
                for (var i=0;i<data.length;i++){
                  $('<option/>').val(data[i]).html(data[i]).appendTo('#id_marca');
                };
            } else {
                alert("No se encontraron marcas con el estilo que nos esta dando, intente con otro estilo !");
                $('#id_pagina').val('0');
            };

            console.log(data);
          },
          error: function(){ 
            alert("Error al devolver el llamado ajax");
          },

        });
                              

      });


      // ***********************************
      // Logica para llenar combo de colores
      // ************************************ 

      $('#id_marca').change(function(){
        
        // Si cambia la marca llena con blancos elementos subsecuentes
        $('#id_talla').empty();
        
        // Inicializa variables que se pasaran al servidor 
        // para la busqueda de las marcas
        
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $('#id_pagina').val();
        id_est = $('#id_estilo').val();

        // ojo: En la siguiente linea la asignacion a la variable "id_mar" debiera
        // funcionar con la sentencia id_est = $('this').val() dado que 
        // me encuentro dentro de #id_marca,sin
        // embargo no funciono. arrojaba el error http 1.1 500
        // lo cambie a como sigue y funciono, checar.

        id_mar = $('#id_marca').val(); //  <-- ojo

        
        
        $.ajax({
          
          url: '/pedidos/combo_colores/',
          type: 'GET',
          data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar},
          success: function(data){
            $('#id_color').empty(); // vacia el combo color para que reciba nuevos valores
              if (data[0] != undefined ) { 
                for (var i=0;i<data.length;i++){
                  $('<option/>').val(data[i]).html(data[i]).appendTo('#id_color');
                };
            } else {
                alert("No se encontraron colores bajo la marca que nos esta dando, intente con otro estilo !");
                $('#id_pagina').val('0');
            };

            console.log(data);
          },
          error: function(){ 
            alert("Error al devolver el llamado ajax");
          },

        });
                              

      });


      // ***********************************
      // Logica para llenar combo de talla
      // ************************************ 

      $('#id_color').change(function(){
        
        // Si cambia el color llena con blancos elementos subsecuentes
        $('#id_talla').empty();
        
        // Inicializa variables que se pasaran al servidor 
        // para la busqueda de las marcas
        //alert('cambio el color')
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $('#id_pagina').val();
        id_est = $('#id_estilo').val();
        id_mar = $('#id_marca').val();

        // ojo: En la siguiente linea la asignacion a la variable "id_mar" debiera
        // funcionar con la sentencia id_est = $('this').val() dado que 
        // me encuentro dentro de #id_marca,sin
        // embargo no funciono. arrojaba el error http 1.1 500
        // lo cambie a como sigue y funciono, checar.

        id_col = $('#id_color').val(); //  <-- ojo

        
        
        $.ajax({
          
          url: '/pedidos/combo_tallas/',
          type: 'GET',
          data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar,'id_col':id_col},
          success: function(data){
            $('#id_talla').empty(); // vacia el combo talla para que reciba nuevos valores
              if (data[0] != undefined ) { 
                for (var i=0;i<data.length;i++){
                  $('<option/>').val(data[i]).html(data[i]).appendTo('#id_talla');
                };
            } else {
                alert("No se encontraron tallas bajo la marca que nos esta dando, intente con otro estilo !");
                $('#id_pagina').val('0');
            };

            console.log(data);
          },
          error: function(){ 
            alert("Error al devolver el llamado ajax en combo talla");
          },

        });
                              

      });


      // Logica para esconder o mostrar el campo id_tallaalt dependiendo del valor de id_talla.

      $('#id_talla').change(function(){

        if($(this).val() == "NE")
        {
            $("#id_tallaalt").show();
        }
        else
        {
            $("#id_tallaalt").hide();
        };
      });



      

      // ***********************************
      // Logica grabar el articulo en temporal con ajax
      // ************************************ 

      $('#grabar').click(function(){
        
        
        // Inicializa variables que se pasaran al servidor 

        var lsuc = '';
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $('#id_pagina').val();
        id_est = $('#id_estilo').val();
        id_mar = $('#id_marca').val();
        id_col = $('#id_color').val(); 
        id_talla = $('#id_talla').val();
        id_tallaalt = $('#id_tallaalt').val();
        descontinuado = 0;
        plazoentrega = $('#id_plazoentrega').val();
        opcioncompra = $('#id_opcioncompra').val();
        fechamaximaentrega = $('#id_fechamaximaentrega').val();
        precio_cliente = $('#id_precio').val();


               

        hayerror = 0;

        var fmaximaentrega_ok = true
        fmaximaentrega_ok=valida_fechamaximaentrega();
        
        if (id_prov == undefined || id_temp == undefined || id_talla == '' || id_talla == 'SELECCIONE...' || id_cat == undefined || id_pag == undefined || id_est == undefined || id_mar == undefined || id_col == undefined || id_talla == undefined || ! fmaximaentrega_ok)
         { 
           if(! fmaximaentrega_ok)
           {
              alert("Si el plazo de entrega será por una 'Fecha' asegurese de ingresar una fecha válida en el campo 'fecha máxima de entrega'. ");
           }

           else {
              alert("Debe seleccionar valores válidos del producto antes de elegirlo !,");
                }
                    
           hayerror = 1;
          }              
           // de otra manera entoces graba registro en tmp.
        else if(id_talla == 'NE' && id_tallaalt.trim() == ''){
             alert("En artículo no especifica la talla, por favor ingrese una talla alternativa !");
              hayerror = 1;
             }

              else {
                   
                    console.log("valores perdidos ojo:");
                    console.log(plazoentrega);
                    console.log(opcioncompra);
                  

                    $.ajax({
                      
                      url: '/pedidos/grabar_pedidos/',
                      type: 'POST',
                      data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar,'id_col':id_col,'id_talla':id_talla,'id_tallaalt':id_tallaalt,'descontinuado':descontinuado,'opcioncompra':opcioncompra,'plazoentrega':plazoentrega,'fechamaximaentrega':fechamaximaentrega,'precio_cliente':precio_cliente},
                      datatype:'application/json',
                      //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                      success: function(data){
                          
                          // Si la talla es blanco es porque dan clic en boton 'elegir' sin antes haber
                          // seleccionado todos los campos.
                          

                            // La siguiente linea de codigo agrega una linea a la tabla carrito, observar dos cosas:
                            // 1.) La primera que se agrega a cada renglon un identificador igual al numero de id de la tabla pedidos_pedidos_tmp, esto
                            //     para facilitar el identificar cada renglon con jquery.
                            // 2.) Cada renglon se clasifica con "deletelink" al final, esto para que posteriormmente el script que borra
                            //     renglones pueda hacer uso de el.

                            //$("#cesto").append("<tr id='"+ data.id+"'><td>"+ data.id +"</td><td>"+ data.id_pag +"</td><td>"+ data.id_est +"</td><td>"+ data.id_mar +"</td><td>"+ data.id_col +"</td><td>"+ data.id_talla +"</td><td>"+ data.precio +"</td>"+"<td><input type='checkbox' class='case'/></td></tr>");
                            console.log(data);
                            if(data.id_talla == 'NE') { talla_var = data.id_tallaalt;
                             } else { talla_var = data.id_talla;
                                };
                            console.log(data.descontinuado);

                            if(data.descontinuado == '1') {alert("Este articulo esta descontinuado, los artículos  descontinuados difícilmente se logra encontrarlos con nuestros proveedores,  el articulo de todos modos se agregará a la lista de pedido, pero Ud. puede  eliminarlo posteriormente.");};

                            $("#cesto").append("<tr id='"+ data.id+"'><td>"+ data.id +"</td><td>"+ data.id_pag +"</td><td>"+ data.id_est +"</td><td>"+ data.id_mar +"</td><td>"+ data.id_col +"</td><td>"+talla_var+"</td><td class='precio' align='right'>"+ data.precio +"</td>"+"<td><button id='but1' class='delete'>Eliminar</button></td></tr>");
                            
                            // Incrementa el contador de articulos a pedir

                            $("#contador").html(function(i, val) { return val*1+1 });

                            // Incrementa el monto total de la orden


                            $("#grantotal").html(function(i, val) { return val*1 + parseInt(data.precio) });

                            // Si hay un elemento en el carrito vuelve a habilitar el combo sucursal.
                          
                            $("#procesar").prop('disabled', false);
                            $("#sucursal").prop('disabled', false);
                             if (data.is_staff == true){
                                          $("#viasolicitud_id").prop('disabled',false);
                                          $('#tiposervicio_id').prop('disabled',false);
                                          $('#anticipo_id').prop('disabled',false);
                                          $('#usr_id').prop('disabled',false);
                                                }
                            
                          // Vacia combo de sucursal

                          // elimina un renglon duplicado
                          //var seen = {};
                          //$('table tr').each(function() {
                          //    var txt = $(this).text();
                          //         if (seen[txt]){
                          //              $(this).remove();
                          //              $("#contador").html(function(i, val) { return val*1-1 });
                          //            }
                          //
                          //          else
                          //                seen[txt] = true;
                          //});

                          
                          

                          //alert(data.id_col);
                          if(hayerror == 0){
                            inicializa_combos();


                          /// LLamado a ajax para llenar combo sucursales

                          /// Este llamado se hace estando dentro del otro ajax.....
                          /// segun esto llamados multiples de ajax se hacen aninados.

                            $.ajax({
                        
                                url: '/pedidos/llena_combo_sucursal/',
                                type: 'GET',
                                data:{'lsuc':lsuc},
                                success: function(data){
                                  //alert("Entro a succes en ajax llena combo sucursal");
                                  console.log(data);
                                  $('#sucursal').empty(); // vacia el combo talla para que reciba nuevos valores
                                    if (data[0] != undefined ) { 
                                      for (var i=0;i<data.length;i++){
                                        $('<option/>').val(data[i]).html(data[i]).appendTo('#sucursal');
                                      };
                                    }

                                    else {
                                      alert("No se encontraron sucursales !");
                                    };

                                  
                                },
                                error: function(){ 
                                  alert("Error al devolver el llamado ajax llenar_combo_sucursal");
                                },

                              });

                          };
              

                                      
                      },
                      error: function(){ 
                        alert("Error al devolver el llamado ajax en grabar pedido");
                      },

                    });
                  };
        
                                

      });

      


    // ELIMINA UN RENGLON DE LA TABLA DEL CARRITO (procedimiento con checkbox..)

    //  function select_all() {
    //  $('input[class=case]:checkbox').each(function(){ 
    //    if($('input[class=check_all]:checkbox:checked').length == 0){ 
    //      $(this).prop("checked", false); 
    //   } else {
    //      $(this).prop("checked", true); 
    //        } 


            
    //    });
    //  }

    //  $(".delete").on('click', function() {
    //                    $('.case:checkbox:checked').parents("tr").remove();

    //                          });

    // Procedimiento con click en boton 'ELIMINAR'

      $('#TablaCarrito').on('click', '.delete', function () {
          
          // recoge el id del articulo para buscarlo en la tabla tmp y eliminarlo
          id_art = $(this).closest('tr').attr('id');

          var precio_articulo = 0;
          var total_orden = 0;
          
          // Remueve el renglon de la tabla html.
          $(this).closest('tr').remove();

          // Recalcula el total de la orden sumando los renglones que quedaron vivos.

          $('#cesto tr').each(function() {
             
            // Trae el valor del precio
             precio_articulo = parseInt($(this).find(".precio").html());
             // Si el valor del precio no es numero entonces le asigna un cero, de lo 
             // contrario habria problemas para calcular la sumatoria total ya que trataria de
             // sumar alfanumericos con numeros.
             if(isNaN(precio_articulo)){
              precio_articulo=0;
             }
             //Acmula el precio al total de la orden
             total_orden += parseInt(precio_articulo);
             console.log(precio_articulo);    
          });

          console.log("el valor de Total orden:");
          console.log(total_orden);

          // Asigna al elemento html el valor del total de la orden
          $("#grantotal").html(total_orden);

          

          //Decrementa el contador de articulos a pedir
          $("#contador").html(function(i, val) { return val*1-1 });
                          

          $.ajax({
          
          url: '/pedidos/eli_reg_tmp/',
          type: 'POST',
          data:{'id_art':id_art},
          datatype:'application/json',
          //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
          success: function(data){

                            
              console.log(data);
              inicializa_combos();

              
          },
          error: function(){ 
            console.log(data);
            alert("Error al eliminar articulo de tabla temporal");
          },

        });







          


          
          console.log('click');
      })

      
      



      // Procesamiento del pedido.





      $("#procesar").click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;
        console.log($("#anticipo_id").val());
        var var_anticipo = parseInt($("#anticipo_id").val())
        var var_gtotal = parseInt($("#grantotal").html());
        console.log(var_gtotal);
        if(var_anticipo > var_gtotal){
                    alert("El anticipo no puede ser mayor al monto del pedido !");
                    continuar_procesando = 0;
        }
        else{
          continuar_procesando = 1;
        

        // valida que se haya seleccionado un valor valido para sucursal

          if($("#sucursal").val().trim() == "GENERAL") {
                          alert("Seleccione la sucursal donde recogerá su pedido !");
                          continuar_procesando = 0;
                       }
                       else{

                        console.log("estado de staff:")
                        console.log(is_staff)

                         if (is_staff == true){

                                            if(num_usr_valido == 0 ){                                       
                                                                //alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                                                                continuar_procesando = 0;
                                              }

                                              else { 

                                                    if (tiene_derecho == 0){
                                                                  //alert("Ud no tiene derechos como empleado para hacer pedidos !")
                                                                  continuar_procesando = 0
                                                    }
                                                    else {

                                                                  alert("Ud. eligió que su pedido le sea entregado en la sucursal " + $("#sucursal").val());
                                                                  continuar_procesando = 1;

                                                    };




                                                      
                                              };  



                                        
                          }              
                          else {

                                              alert("Ud. eligió que su pedido le sea entregado en la sucursal " + $("#sucursal").val());
                                              continuar_procesando = 1;
                          };



                      };

                        
                       
        };

        if(continuar_procesando == 1){             

          e.preventDefault();
          var answer=confirm('Su pedido va a ser procesado, Si está seguro que la sucursal de entrega,los artículos y demás datos del pedido son correctos acepte, caso contrario cancele y corrija.');
            if(answer){

                    lsuc = $('#sucursal').val();
                    tiposerv = $('#tiposervicio_id').val()
                    viasolic = $('#viasolicitud_id').val()
                    anticipo = $('#anticipo_id').val()
                    
                    //  Al total se le asigna el html y no un val() dado que este id corresponde a una etiqueta, no a un elemento como un input o un select que si manejan el atributo value 
                    total = $('#grantotal').html() 

                    $.ajax({

                     url: '/pedidos/procesar_pedido/',
                      type: 'POST',
                      data: {'lsuc':lsuc,'tiposervicio':tiposerv,'viasolicitud':viasolic,'anticipo':anticipo,'total':total,'usr_id':$("#usr_id").val()},
                      datatype:'application/json',
                      //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                      success: function(data){

                                        
                          console.log(data);

                          if (data.status_operacion != 'ok') { 
                            alert("Error: Su pedido no pudo ser procesado, vuelva a intentar !");
                            }
                          else {
                            alert("Pedido grabado con número "+data.PedidoNuevo+", puede dar seguimiento en consulta de pedidos.");
                            $( "#idpedido" ).html(data.PedidoNuevo);
                            $( "#idpedido" ).val(data.PedidoNuevo);   
                                

                            }; 
                          $("#cesto").empty();
                          $("#contador").empty();
                          $("#grantotal").empty();
                          $("#anticipo_id").val(0)
                          $("#procesar").prop('disabled', true);
                          $("#idpedido").prop('disabled',false);

                          


                          
                                      
                      },
                      error: function(){ 
                        console.log(data);
                        
                      },

                    });




             
            }
            
        }

      });



      /*   EJEMPLO DE BLUR
      $("#id_fechainicial").blur(function(){
        alert("This input field has lost its focus.");
        }); */

    $('#procesar_recepcion').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;
        
        e.preventDefault();
        var answer=confirm('Su cambios van a ser procesados, registros por procesar: '+reg_encontrados+'. Si está seguro son correctos acepte, caso contrario cancele y modifique.');
          if(answer){

                  var TableData;
                  TableData = storeTblValues2();
                  console.log(TableData)
                  //TableData = $.toJSON(TableData);
                  TableData = JSON.stringify(TableData);
                  console.log("EN FORMATO JSON:");
                  console.log(TableData);

                  $("#id_marcartodo_nollego").val()
                  $("#id_nueva_fecha_llegada").val()


                  $.ajax({

                    url: '/pedidos/procesar_recepcion/',
                    type: 'POST',
                    data: {'TableData':TableData,'almacen':almacen,'nueva_fecha_llegada':nueva_fecha_llegada,'marcartodo_nollego':marcartodo_nollego,'cierre':cierre},
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data){

                                      
                        console.log(data);

                        if (data.status_operacion != 'ok') { 
                          alert(data.error);
                          }
                        else {
                          alert("Recepción grabada con éxito !.");
                          }; 
                        $("#procesar_recepcion").prop('disabled', true);
                    },
                    error: function(){ 
                      console.log(data);
                      
                    },

                  });
             
          }
      });







      // PROCESAMIENTO DE COLOCACIONES 


      $('#procesar_colocaciones').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        continuar_procesando = 0;

        if(num_usr_valido == 0 ){                                       
                                //alert ("Código de empleado inválido, ingrese su código de empleado !"); 
                                continuar_procesando = 0;
              }

              else { 

                    if (tiene_derecho == 0){
                                  //alert("Ud no tiene derechos como empleado para hacer pedidos !")
                                  continuar_procesando = 0
                    }
                    else {

                                  
                                  continuar_procesando = 1;

                    }
                  };

        if(continuar_procesando == 1){

        e.preventDefault();
        var answer=confirm('Su cambios van a ser procesados, nuevos registros encontrados por procesar: '+reg_encontrados+'. Si está seguro son correctos acepte, caso contrario cancele y modifique.');
          if(answer){

                  var TableData;
                  TableData = storeTblValues();
                  console.log(TableData)
                  //TableData = $.toJSON(TableData);
                  TableData = JSON.stringify(TableData);
                  console.log("EN FORMATO JSON:");
                  console.log(TableData);
                  $.ajax({

                    url: '/pedidos/procesar_colocaciones/',
                    type: 'POST',
                    data: {csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),'TableData':TableData,'almacen':almacen,'usr_id':$("#usr_id_colocaciones").val(),'fecha_probable':$("#id_fecha_probable").val()},
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data){
                      
                                      
                        console.log(data);

                        if (data.status_operacion != 'ok') { 
                          alert(data.error);
                          }
                        else {
                          alert("Colocaciones grabadas con exito !.");
                          if (data.pedidos_no_procesados != ''){
                          alert(data.pedidos_no_procesados);  
                          } 
                          
                          }; 
                        $("#procesar_colocaciones").prop('disabled', true);
                    },
                    error: function(data){ 
                      
                      console.log(data);
                      console.log(data.status_operacion);
                      
                    },

                  });
             
          }
        }
      });


      // PROCESAMIENTO DE CIERRE DE PEDIDO

      $('#procesar_cierre_pedido').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;

        referencia = $('#id_referencia').val();
        total_articulos = $('#id_total_articulos').val();
        colocado_via = $('#id_colocado_via').val();
        tomado_por = $('#id_tomado_por').val();
        confirmado_por = $('#id_confirmado_por').val();
        fecha_cierre = $('#id_fecha_cierre').val();
        hora_cierre = $('#id_hora_cierre').val();
        fecha_llegada =  $('#id_fecha_llegada').val();
        pedido = $("#id_pedido").val();
        importe = $("#id_importe").val();
        importe_nc = $("#id_importe_nc").val();
        monto_pagar =  $('#id_monto_pagar').val();
        paqueteria = $('#id_paqueteria').val();
        no_de_guia = $('#id_no_de_guia').val();
        usr_id = $("#usr_id_colocadosacerrar").val();

        // comienza validacion de campos antes de pasar al servidor

        if (referencia.length < 3 ){
          //alert("La longitud de la referencia debe ser de al menos 3 caracteres !")
          continuar_procesando = 1
        }
        else{
          if(tomado_por.length < 3){
            alert(" 'Tomado por ' debe tener al menos 3 caracteres !")
            continuar_procesando = 0
          }
          else{
            if(confirmado_por.length < 3 ){
              alert(" 'Confirmado por ' debe tener al menos 3 caracteres !")
              continuar_procesando = 0
            }
            else {
              if (fecha_llegada < (new Date())){
                alert(" Ingrese una fecha de llegada mayor a hoy !")
                continuar_procesando = 0
              }
              else{
                if(pedido <= 0){
                  alert(" Ingrese un numero de pedido mayor a cero !")
                  continuar_procesando = 0

                }
                else { 
                  if( importe <= 0){
                    alert(" Ingrese un importe mayor a cero !")
                    continuar_procesando = 0
                  }
                  else{
                    if (paqueteria.length < 3){
                      alert(" 'Paqueteria' debe ser de al menos 3 caracteres !")
                      continuar_procesando = 0
                    } else {
                      if (no_de_guia.length < 3){
                        //alert(" 'Numero de guia ' debe ser de al menos 3 caracteres !")
                        continuar_procesando = 1
                      } else {
                        if(total_articulos <= 0){
                          alert("Total de articulos debe ser mayor a cero !")
                          continuar_procesando = 0
                        } else {
                        continuar_procesando = 1
                       }
                      }
                    }
                  }
                }
              }
            }
          }
        }

        if(continuar_procesando == 1){

        
        e.preventDefault();
        var answer=confirm('Se procederá a cerrar el pedido, si está seguro que todo es correcto acepte, caso contrario cancele y modifique.');
          if(answer){

                  var TableData;
                  TableData = storeTblValues_1();
                  console.log(TableData)
                  //TableData = $.toJSON(TableData);
                  TableData = JSON.stringify(TableData);
                  console.log("EN FORMATO JSON:");
                  console.log(TableData);
                  $.ajax({

                    url: '/pedidos/procesar_cierre_pedido/',
                    type: 'POST',
                    data: {'TableData':TableData,'almacen':almacen,'referencia':referencia,'total_articulos':total_articulos,'colocado_via':colocado_via,'confirmado_por':confirmado_por,'tomado_por':tomado_por,'fecha_cierre':fecha_cierre,'hora_cierre':hora_cierre,'fecha_llegada':fecha_llegada,'pedido':pedido,'importe':importe,'importe_nc':importe_nc,'monto_pagar':monto_pagar,'paqueteria':paqueteria,'no_de_guia':no_de_guia,'proveedor':proveedor,'usr_id':usr_id,},
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data){

                                      
                        console.log(data);

                        if (data.status_operacion != 'ok') { 

                          alert(data.error);
                          }
                        else {
                          alert("Cierre grabado con exito !.");
                          $("#procesar_cierre_pedido").prop('disabled', true);
                          }; 
                        
                    },
                    error: function(){ 
                      console.log(data);
                      
                    },

                  });
             
          }
        }
      });


    // PROCESAR VENTAS //
//$("#procesar_venta").prop('disabled',true);



$('#procesar_ventas').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;
        var tot_gral = $('#totalgral').text();
        var recibido = $('#input_recibido').val();// A este control el cual es un input
                                                  // a diferencia del anterior que no es input
                                                  // debe aplicarsele el metodo val() en lugar
                                                  // del .text() o el .html(), de lo contrario
                                                  // no se traera su valor y la variable "recibido"
                                                  // queda en blanco.


        console.log(tot_gral)
        console.log(recibido)

        //$("#").prop('disabled',true);
        if (parseInt(recibido) < parseInt(tot_gral) && parseInt(tot_gral) > 0 ) {
                alert("Lo recibido debe cubrir el total !")
        } else {
              if(parseInt($("#usr_id_colocadosacerrar").val())<=0){
                    alert("Ingrese un codigo de empleado !");
                    continuar_procesando = 0;
              } else {
                  continuar_procesando = 1
                }

          
        }

        if (parseInt(recibido) > parseInt(tot_gral) && parseInt(tot_gral) > 0 ){

            alert("Vuelto: "+(parseInt(recibido) - parseInt(tot_gral)).toString())
        }


        //if($("#usr_id_colocadosacerrar").html() <= 0){
        //        alert("Ingrese codigo de usuario ! ");
                //$("#procesar_ventas").prop('disabled', true);
        //        continuar_procesando = 0;
        //} else{
        //  continuar_procesando = 1;
        //}

        


        if (continuar_procesando == 1) {
          e.preventDefault();
          var answer=confirm('Su venta va a ser procesada, Si está seguro acepte, caso contrario cancele y modifique.');
            if(answer){

                    
                  // Prepara la tabla de ventas a pasar via ajax
                    var TableData_ventas;
                    TableData_ventas = storeTblValues_ventas();
                    console.log(TableData_ventas)
                    //TableData = $.toJSON(TableData);
                    TableData_ventas = JSON.stringify(TableData_ventas);



                    console.log("EN FORMATO JSON:");
                    console.log(TableData_ventas);



                    // Prepara la tabla de creditos a pasar via ajax
                    var TableData_creditos;
                    TableData_creditos = storeTblValues_creditos();
                    console.log(TableData_creditos)
                    //TableData = $.toJSON(TableData);
                    TableData_creditos = JSON.stringify(TableData_creditos);
                    var totalcreditos = $("#totalcreditos").text()
                    var totalventas = $("#totalventas").text()
                    var totalcargos = $("#totalcargos").text()
                    var totaldsctos = $("#totaldsctos").text()
                    var totalgral = $("#totalgral").text()
                    // LA SIGUIENTE LINEA SIRVE PARA CAPTURAR EL CODIGO DEL CAPTURISTA 
                    // Y MANDARLO VIA AJAX A VIEWS, SE UTILIZA IGUAL QUE
                    // EN CIERRE DE PEDIDOS PARA NO TIRAR TANTO CODIGO.

                    var usr_id = $("#usr_id_colocadosacerrar").val();



                    // Prepara la tabla de cargos a pasar via ajax
                    var TableData_cargos;
                    TableData_cargos= storeTblValues_cargos();
                    console.log(TableData_cargos)
                    //TableData = $.toJSON(TableData);
                    TableData_cargos = JSON.stringify(TableData_cargos);

                               



                    $.ajax({

                      url: '/pedidos/procesar_venta/',
                      type: 'POST',
                      data: {'TableData_ventas':TableData_ventas,'TableData_creditos':TableData_creditos,'TableData_cargos':TableData_cargos,'totalcreditos':totalcreditos,'totalventas':totalventas,'totalcargos':totalcargos,'totaldsctos':totaldsctos,'totalgral':totalgral,'id_socio':id_socio,'recibido':recibido,'usr_id':usr_id,},
                      datatype:'application/json',
                      //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                      success: function(data){

                                        
                          console.log(data);

                          if (data.status_operacion != 'ok') { 
                            alert(data.error);
                            }
                          else {
                            
                            
                            $("#idventa").html(data.nodocto);
                            $("#idventa").val(data.nodocto);
                            $("#id_credito_nuevo").html(data.nueva_nota_credito);
                            $("#id_credito_nuevo").val(data.nueva_nota_credito);

                            alert("venta grabada con éxito !.");
                            $("#procesar_ventas").prop('disabled', true);

                            }; 
                          
                      },
                      error: function(){ 
                        console.log(data);
                        
                      },

                    });
               
            }

        }
        });
      








                     
      // Las dos siguientes funciones se utilizan
      // para cuando usamos ajax con POST y vamos
      // a alterar informacion del sistema.
      // Por cierto, la pruebas que se hicieron con POST
      // arrojaban invariablemente el error http 1.1 500
      // Nunca pude hacer retornar los valores de los combos

      // Funcion para traer cookie de la sesion

          
      // using jQuery
      function getCookie(name) {
          var cookieValue = null;
          if (document.cookie && document.cookie != '') {
              var cookies = document.cookie.split(';');
              for (var i = 0; i < cookies.length; i++) {
                  var cookie = jQuery.trim(cookies[i]);
                  // Does this cookie string begin with the name we want?
                  if (cookie.substring(0, name.length + 1) == (name + '=')) {
                      cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                      break;
                  }
              }
          }
          return cookieValue;
      }
      var csrftoken = getCookie('csrftoken');

      function csrfSafeMethod(method) {
      // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      }

      $.ajaxSetup({
          beforeSend: function(xhr, settings) {
              if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                  xhr.setRequestHeader("X-CSRFToken", csrftoken);
              }
          }
      });   


      // PICK_LIST SOCIO

    $('#buscar_picklistsocio').click(function(event){
               //alert("hola");
                event.preventDefault();
                $.ajax({
                        url: '/pedidos/picklist_socio',
                        type: 'GET',
                        data: {'string_a_buscar':$('#input_nom_socio').val()},
                        success: function(data,total_elementos) {
                            console.log(data);
                            var tableData = ''

                            $('tbody').empty(); // Borra tabla

                            if (data.length==0){
                                alert("No se encontraron coincidencias !")
                            };
                            //tableData += "<thead><tr><th>id</th><th>Ap paterno</th><th>Ap materno</th><th>Nombre</th></tr></thead>"; // Dibuja encab
                            //Ajax nos retorna en data un arreglo de arreglos..asi
                            // que primeramente "each(data....)" hace referecia a 
                            // cada arreglo dentro del arreglo y "value" nos trae
                            // el conenido de cada arreglo, asi que tenemos que hacer
                            // referencia a value[0], value[1]... etc para poder traer los campos que nos interesan.

                            $('tbody').append(
                                $.each(data, function(key,value){
                                                                        
                                    tableData += '<tr>';
                                    tableData += '<td>' +value['AsociadoNo']+'</td>'; // link id para modificar.
                                     tableData += '<td>' + value['ApPaterno'] + '</td>';
                                     tableData += '<td>' + value['ApMaterno'] + '</td>';
                                     tableData += '<td>' + value['Nombre'] + '</td>';
                                                   
                                     
                                     
                                    tableData += '</tr>';
                                    
                                })
                            );
                            $('#tot').text("Total de registros encontrados: "+data.length);
                            $('tbody').html(tableData); // Cambi el contenido de tbody
                            
                        },

                        error: function(data) {
                            console.log('error')
                            console.log(data)
                        }
                });
             }) 



    // PICK_ESTILOS_PAGINA

    $('#buscar_estilopagina').click(function(event){
               //alert("hola");
                event.preventDefault();
                $.ajax({
                        url: '/pedidos/picklist_estilopagina',
                        type: 'GET',
                        data: {'estilo_a_buscar':$('#input_estilo').val(),'proveedor':$('#id_proveedor').val(),'temporada':$('#id_temporada').val(),'catalogo':$('#id_catalogo').val()},
                        success: function(data,total_elementos) {
                            console.log(data);
                            var tableData = ''

                            $('#estilopagina').empty(); // Borra tabla

                            if (data.length==0){
                                alert("No se encontraron coincidencias !")
                            };
                            //tableData += "<thead><tr><th>id</th><th>Ap paterno</th><th>Ap materno</th><th>Nombre</th></tr></thead>"; // Dibuja encab
                            //Ajax nos retorna en data un arreglo de arreglos..asi
                            // que primeramente "each(data....)" hace referecia a 
                            // cada arreglo dentro del arreglo y "value" nos trae
                            // el conenido de cada arreglo, asi que tenemos que hacer
                            // referencia a value[0], value[1]... etc para poder traer los campos que nos interesan.

                            $('#estilopagina').append(
                                $.each(data, function(key,value){
                                                                        
                                    tableData += '<tr>';
                                    tableData += '<td class="campo">' +value['estilo']+'</td>'; // link id para modificar.
                                    tableData += '<td class="campo">' + value['pagina'] + '</td>';
                                    tableData += '<td class="campo">' + value['precio'] +'</td>';                 
                                     
                                     
                                    tableData += '</tr>';
                                    
                                })
                            );
                            $('#tot').text("Total de registros encontrados: "+data.length);
                            $('#estilopagina').html(tableData); // Cambi el contenido de tbody
                            
                        },

                        error: function(data) {
                            console.log('error')
                            console.log(data)
                        }
                });
             }) 

    $('#muestra_colocaciones_form').submit(function(e){
      
      
      // Inicializa variables que se pasaran al servidor 

      var lsuc = '';
      x_proveedor = $('#id_proveedor').val();
      x_almacen = $('#id_almacen').val();
      x_tipo_consulta = $('#id_consultar_pedidos').val();
      x_fechainicial = $('#id_fechainicial').val();
      x_fechafinal = $('#id_fechafinal').val();

     hayerror = 0;

             
      if (x_proveedor == '0' ||  x_fechainicial == '' || x_fechafinal=='')
       { 
         
         alert("Debe seleccionar valores válidos para los campos antes de solicitar la consulta !.");
         e.preventDefault();

    
                  
         hayerror = 1;
        }              
         // valida fecha maxima vs fecha minima.
      else { 
            //if(new Date(x_fechafinal).getTime() < new Date(x_fechainicial).getTime()){
            if(Date.parse(x_fechafinal)< Date.parse(x_fechainicial)){
                alert("La fecha final no puede ser menor a la fecha inicial, por favor rectifique !");
                hayerror = 1;
              e.preventDefault();
            

              }
              // de otra manera hace el llamado a ajax para desplegar registros
            else {
                  var xx=10;
                  } 
             
            }  
          }); 

       




      //*********************************
      // Logica mostrar tabla de colocaciones (no se utiliza, se hace via form POST)
      // ************************************ 

    $('#xbtn_trae_colocaciones').click(function(){
      
      
      // Inicializa variables que se pasaran al servidor 

      var lsuc = '';
      proveedor = $('#id_proveedor').val();
      almacen = $('#id_almacen').val();
      tipo_consulta = $('#id_consultar_pedidos').val();
      fechainicial = $('#id_fechainicial').val();
      fechafinal = $('#id_fechafinal').val();


     

      hayerror = 0;

             
      if (proveedor == undefined || almacen == undefined || fechainicial == '' || fechafinal=='')
       { 
         
         alert("Debe seleccionar valores válidos del producto antes de elegirlo !,");
              
                  
         hayerror = 1;
        }              
         // valida fecha maxima vs fecha minima.
      else { 
            if(fechafinal < fechainicial){
                alert("La fecha final no puede ser menor a la fecha inicial, por favor rectifique !");
                hayerror = 1;
              }
              // de otra manera hace el llamado a ajax para desplegar registros
            else {
                 
                 $.ajax({
                    
                    url: '/pedidos/muestra_colocaciones/',
                    type: 'GET',
                    data:{'proveedor':id_prov,'almacen':almacen,'fechainicial':fechainicial,'fechafinal':fechafinal,'tipo_consulta':tipo_consulta,},
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data)
                      {
                        console.log(" los datos retornados de colocaciones:");
                        console.log(data);
                        
                          
                          $("#CuerpoColocaciones").append("<tr id='"+ data.id+"'><td>"+ data.id +"</td><td>"+ data.id_pag +"</td><td>"+ data.id_est +"</td><td>"+ data.id_mar +"</td><td>"+ data.id_col +"</td><td>"+talla_var+"</td><td class='precio' align='right'>"+ data.precio +"</td>"+"<td><button id='but1' class='delete'>Eliminar</button></td></tr>");
                          

                     },
                    error: function(){ 
                      alert("Error al devolver el llamado ajax en grabar pedido");
                    },

                  });
                };
            };
    });  



// RUTINA PARA CANCELAR UN PEDIDO



        $('.btn_cancela_pedido').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;
        
        e.preventDefault();
        var answer=confirm('Se procederá a cancelar el registro, si está seguro de clic en "aceptar", caso contrario de clic en "cancelar".');
          if(answer){


                 var motivo = prompt("Por favor ingrese el motivo de la cancelacion:", "Cancelacion");
                
                 pedido = $(this).parents('tr').find('td:eq(0)').text();
                 productono = $(this).parents('tr').find('td:eq(1)').text();
                 catalogo = $(this).parents('tr').find('td:eq(2)').text();
                 nolinea = $(this).parents('tr').find('td:eq(3)').text(); 
                  //TableData = $.toJSON(TableData);
                  //TableData = JSON.stringify(TableData);
                  
                  $.ajax({

                    url: '/pedidos/cancelar_pedido/',
                    type: 'POST',
                    data: {'motivo':motivo,'pedido':pedido,'productono':productono,'catalogo':catalogo,'nolinea':nolinea },
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data){

                                      
                        console.log(data);

                        if (data.status_operacion != 'ok') { 
                          alert(data.error);
                          }
                        else {
                          alert("Cancelacion exitosa !.");
                          

                          }; 
                        //$("#procesar_recepcion").prop('disabled', true);
                    },
                    error: function(){ 
                      console.log(data);
                      
                    },

                  });
             
          }
      });


     $('#procesar_devolucion_socio').click(function(e){

        // valida que el anticipo sea menor al monto del pedido.
        // observar que se puede comparar un contenido html con un valor
        // al menos aqui si hace la comparacion.
        
        continuar_procesando = 0;
        
        e.preventDefault();
        var answer=confirm('Su cambios van a ser procesados, Si está seguro acepte, caso contrario cancele.');
          if(answer){

                  var TableData;
                  TableData = storeTblValues_dev_socio();
                  console.log(TableData)
                  //TableData = $.toJSON(TableData);
                  TableData = JSON.stringify(TableData);
                  console.log("EN FORMATO JSON:");
                  console.log(TableData);

                  $("#id_marcartodo_nollego").val()
                  $("#id_nueva_fecha_llegada").val()
                  var usr_id = $("#usr_id_pedidos_recepcionar").val();


                  $.ajax({

                    url: '/pedidos/procesar_devolucion_socio/',
                    type: 'POST',
                    data: {'TableData':TableData,'socio':socio,'usr_id':usr_id,'tipoconsulta':tipoconsulta},
                    datatype:'application/json',
                    //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                    success: function(data){

                                      
                        console.log(data);

                        if (data.status_operacion != 'ok') { 
                          alert(data.error);
                          }
                        else {
                          $("#id_nuevo_credito").val(data.nuevo_credito);

                          alert("Devolucion grabada con éxito !.");
                          }; 
                        $("#procesar_devolucion_socio").prop('disabled', true);
                    },
                    error: function(){ 
                      console.log(data.error);
                      
                    },

                  });
             
          }
      });

     $('#id_doc_ventadecatalogo').change(function(){ //1


                        if ($('#id_doc_ventadecatalogo').val() != '0') { 


                            $("#id_doc_temporada").prop('disabled', false);
                            $("#id_doc_anio").prop('disabled', false);
                            $("#id_doc_proveedor").prop('disabled', false);
                          
                          }
                        else {
                            $("#id_doc_temporada").prop('disabled', true);
                            $("#id_doc_anio").prop('disabled', true);
                            $("#id_doc_proveedor").prop('disabled', true);
                          
                                  // alert("Devolucion grabada con éxito !.");
                          }; 



     });


                            

 });





                   
    

    
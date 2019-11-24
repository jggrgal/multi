
    
  
    // 
    
    $(document).ready(function() {
       
       var id_temp = ''
       var id_prov = ''
       var id_cat = ''
       var id_pag = ''
       var id_art = 0
       var continuar_procesando =0

       var total_articulos_pedidos = 0
       

       $("#procesar").prop('disabled', true);
       $("#sucursal").prop('disabled', true);

       

        // La funcion es para ver que funciona JavaScript y va amarrada al tag
        // msgid que esta en el template "index", para probar hay que descomentar aqui y en 
        // el template index.

       //$("#msgid").html("This is Hello World by JQuery");


       // funcion para activar el picker de fecha en consulta_pedidos
      //$('.datepicker').datepicker({dateFormat: "dd/mm/yyyy"});



             

      // Esta funcion lo que hace es lanzar un click en el boton #submcltes
      // del formulario en le template "listaclientes"

      function elimina_clientes(){
        $('#submcltes').trigger('click');
      }
        


      //     Dialogo 
      
        $("#eliminaclientes").click(function(event){
          event.preventDefault();
          $("#dialog-1").dialog({
          modal: true,
          autoOpen: true,
          title: "Advertencia",
          buttons: {CONFIRMAR: function(){ elimina_clientes();},
                    CANCELAR : function() {
                                  $(this).dialog("close");}
                   }

          });  
        });

      // Funcion para inicializar combos

      function inicializa_combos(){

        $('id_proveedor').val(0);
        $('#id_temporada').val('0');
        $('#id_catalogo').val('SELECCIONE...'); 
        $('#id_pagina').val('0');
        $('#id_estilo').val('SELECCIONE...');
        $('#id_marca').val('SELECCIONE...');
        $('#id_color').val('SELECCIONE...');
        $('#id_talla').val('SELECCIONE...');
        $('#id_suc').val(0);
        $('#id_tallaalt').val('');
        


      }




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

      }); 


      
      // ******************************
      // Logica para cuando cambia combo temporada 
      //*******************************

      $('#id_temporada').change(function(){
         
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
          success: function(data){
            
            $('#id_catalogo').empty(); // vacia el combo catalogo preparandolo a recibir nuevos valores.
            
            for (var i=0;i<data.length;i++){
              $('<option/>').val(data[i]).html(data[i]).appendTo('#id_catalogo');
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

        var lsuc = ''
        
        
        id_prov = $('#id_proveedor').val();
        id_temp = $('#id_temporada').val();
        id_cat = $('#id_catalogo').val();
        id_pag = $('#id_pagina').val();
        id_est = $('#id_estilo').val();
        id_mar = $('#id_marca').val();
        id_col = $('#id_color').val(); 
        id_talla = $('#id_talla').val();
        id_tallaalt = $('#id_tallaalt').val();

        hayerror = 0;

        if (id_prov == undefined || id_temp == undefined || id_talla == '' || id_talla == 'SELECCIONE...' || id_cat == undefined || id_pag == undefined || id_est == undefined || id_mar == undefined || id_col == undefined || id_talla == undefined ) { 
           alert("Debe seleccionar valores válidos del producto antes de elegirlo !");
           hayerror = 1;
                        }              
           // de otra manera entoces graba registro en tmp.
        else if(id_talla == 'NE' && id_tallaalt.trim() == ''){
             alert("En artículo no especifica la talla, por favor ingrese una talla alternativa !");
              hayerror = 1;
             }

              else {


                    $.ajax({
                      
                      url: '/pedidos/grabar_pedidos/',
                      type: 'POST',
                      data:{'id_prov':id_prov,'id_temp':id_temp,'id_cat':id_cat,'id_pag':id_pag,'id_est':id_est,'id_mar':id_mar,'id_col':id_col,'id_talla':id_talla,'id_tallaalt':id_tallaalt},
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
                            
                            if(data.id_talla == 'NE') { talla_var = data.id_tallaalt;
                             } else { talla_var = data.id_talla;
                                };

                            $("#cesto").append("<tr id='"+ data.id+"'><td>"+ data.id +"</td><td>"+ data.id_pag +"</td><td>"+ data.id_est +"</td><td>"+ data.id_mar +"</td><td>"+ data.id_col +"</td><td>"+talla_var+"</td><td class='precio' align='right'>"+ data.precio +"</td>"+"<td><button id='but1' class='delete'>Eliminar</button></td></tr>");
                          
                            // Incrementa el contador de articulos a pedir

                            $("#contador").html(function(i, val) { return val*1+1 });

                            // Incrementa el monto total de la orden


                            $("#grantotal").html(function(i, val) { return val*1 + parseInt(data.precio) });

                            // Si hay un elemento en el carrito vuelve a habilitar el combo sucursal.

                            $("#procesar").prop('disabled', false);
                            $("#sucursal").prop('disabled', false); 

                            
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





      $('#procesar').click(function(e){

        // valida que se haya seleccionado un valor valido para sucursal

        if($("#sucursal").val().trim() == "GENERAL") {
                        alert("Seleccione la sucursal donde recogerá su pedido !");
                        continuar_procesando = 0;
                     }
                     else
                     {
                        alert("Ud. eligió que su pedido le sea entregado en la sucursal " + $("#sucursal").val());
                        continuar_procesando = 1;
                     }

        if(continuar_procesando == 1){             

          e.preventDefault();
          var answer=confirm('Su pedido va a ser procesado, Si está seguro que la sucursal de entrega y los artículos son correctos acepte, caso contrario cancele y corrija.');
            if(answer){

                    lsuc = $('#sucursal').val();
                    $.ajax({

                     url: '/pedidos/procesar_pedido/',
                      type: 'POST',
                      data: {'lsuc':lsuc},
                      datatype:'application/json',
                      //csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
                      success: function(data){

                                        
                          console.log(data);

                          if (data.status_operacion != 'ok') { 
                            alert("Error: Su pedido no pudo ser procesado, vuelva a intentar !");
                            }
                          else {
                            alert("Pedido grabado con número "+data.PedidoNuevo+", puede dar seguimiento en consulta de pedidos.");
                          $("#cesto").empty();
                          $("#contador").empty();
                          $("#grantotal").empty();
                          $("#procesar").prop('disabled', true);
                            
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






                   
    });
    
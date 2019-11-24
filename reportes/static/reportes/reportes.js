
    
  
    // Logica para eliminar clientes  
    
    $(document).ready(function() {
       

        // Rutina Para eliminar clientes 
       function elimina_cltes_sin_uso() {
            console.log("Entro a eliminar clientes!") // sanity check
            console.log($('#submcltes').text())
            $.ajax({
              url : "commitdelclientes/", // the endpoint
              type : "POST", // http method
              data : {csrfmiddlewaretoken: '{{ csrf_token }}',
                      id:'{{ id }}'}, // data sent with the post request

              // handle a successful response
              success : function() {
              //    $('#post-text').val(''); // remove the value from the input
              //    console.log(json); // log the returned json to the console
              console.log("success"); // another sanity check
                    },

              // handle a non-successful response
              error : function(xhr,errmsg,err) {
              $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                  " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
              console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
              }
            });
          };

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
                   
    });
    
// Copyright 2016, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function(){
  // This is the host for the backend.
  // TODO: When running Firenotes locally, set to http://localhost:8081. Before
  // deploying the application to a live production environment, change to
  // https://backend-dot-<PROJECT_ID>.appspot.com as specified in the
  // backend's app.yaml file.
  // var backendHostUrl = 'https://backend-dot-fireproto-5c009.appspot.com';
  var backendHostUrl = 'https://synapcards.com';

  // Initialize Firebase
  var config = {
    apiKey: "AIzaSyCOrg4vnNpWniyNPB4_Gy2n0mv5t95DJJI",
    authDomain: "synapcards-178123.firebaseapp.com",
    databaseURL: "https://synapcards-178123.firebaseio.com",
    projectId: "synapcards-178123",
    storageBucket: "synapcards-178123.appspot.com",
    messagingSenderId: "266358714814"
  };


  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {
      if (user) {
        user.getToken().then(function(idToken) {
          /* Now that the user is authenicated, get or add synapcard account */
          $.ajax(backendHostUrl + '/signinajax', {
            /* Set header for the XMLHttpRequest to get data from the web server
            associated with userIdToken */
            headers: {
              'Authorization': 'Bearer ' + idToken
            }
          }).then(function(data){
            $('#signed-in-top').show();
            $('#signed-out-top').hide();

            if ('error_message' in data) {
              console.log("error during account get or add");
              $('#signed-in').hide();
              $('#signed-in-new-user').hide();
              $('#signed-in-existing-user').hide();
              $('#sign-in-error').show();
              $('#sign-in-error-message').text(data.error_message);
              $('#signed-out').hide();
            } else {
              // Everything was successful.
              $('#signed-in').show();
              $('#signed-in-user-id-top').text(data.signed_in_user_id);
              if (data.total_cards > 0) {
                $('#signed-in-new-user').hide();
                $('#signed-in-existing-user').show();
              } else {
                $('#signed-in-new-user').show();
                $('#signed-in-existing-user').hide();
              }
              $('#sign-in-error').hide();
              $('#signed-in-user-id-container').text(data.signed_in_user_id);
              link = backendHostUrl + '/user/' + data.signed_in_user_id;
              $('#self-profile-link').attr('href', link);
              $('#self-profile-link-top').attr('href', link);
              link = backendHostUrl + '/card/' + data.signed_in_user_id + ':0';
              $('#add-new-card-link').attr('href', link);
              $('#signed-out').hide();
            }
          });
        });
      } else {
        // Signed out state.
        $('#signed-in').hide();
        $('#signed-in-top').hide();
        $('#signed-out-top').show();
        $('#signed-in-new-user').hide();
        $('#signed-in-existing-user').hide();
        $('#sign-in-error').hide();
        $('#signed-out').show();
      }
    // [END onAuthStateChanged]
    });
  }

  // [START configureFirebaseLoginWidget]
  // Firebase log-in widget
  function configureFirebaseLoginWidget() {
    var uiConfig = {
      'signInSuccessUrl': '/signin',
      'signInOptions': [
        // Leave the lines as is for the providers you want to offer your users.
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.FacebookAuthProvider.PROVIDER_ID,
        // firebase.auth.TwitterAuthProvider.PROVIDER_ID,
        // firebase.auth.GithubAuthProvider.PROVIDER_ID,
        // firebase.auth.EmailAuthProvider.PROVIDER_ID
      ],
      // Terms of service url
      'tosUrl': '<your-tos-url>',
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }
  // [END configureFirebaseLoginWidget]

  var signOutBtn =$('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();

    firebase.auth().signOut().then(function() {
      console.log("Sign out successful");
    }, function(error) {
      console.log(error);
    });
  });

  configureFirebaseLogin();
  configureFirebaseLoginWidget();

});

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

  // This is passed into the backend to authenticate the user.
  var userIdToken = null;

  // Params from the query portion of the URL
  var queryParams = {};

  // Firebase log-in
  function configureFirebaseLogin() {

    firebase.initializeApp(config);

    // [START onAuthStateChanged]
    firebase.auth().onAuthStateChanged(function(user) {

      parseQueryParams(window.location.search.substr(1));
      fillForm();

      if (window.location.href.split("/").pop() === "search") {
        $('#search-section').hide();
      }

      if (user) {
        user.getToken().then(function(idToken) {
          userIdToken = idToken;
          $('#signed-in-top').show();
          $('#signed-out-top').hide();
          $.ajax(backendHostUrl + '/signinajax', {
            headers: {
              'Authorization': 'Bearer ' + userIdToken
            }
          }).then(function(data){
            userData = data;
            $('#signed-in-user-id-top').text(userData.signed_in_user_id);
            link = backendHostUrl + '/user/' + userData.signed_in_user_id;
            $('#self-profile-link-top').attr('href', link);
          });
        });
      } else {
        // Signed out state.
        $('#signed-in-top').hide();
        $('#signed-out-top').show();
      }
    });
  }

  function parseQueryParams(qstr) {
    var decoded = decodeURIComponent(qstr).replace(/\+/g, ' ');
    console.log("decoded:" + decoded);
    var arr = decoded.split("&");
    for (var i = 0; i < arr.length; i++) {
        var p = arr[i].split("=");
        queryParams[p[0]] = p[1];
        console.log(p[0] + " = " + p[1]);
    }
  }

  function fillForm() {
    console.log("Set user dropdown selected to " + queryParams.user_id);
    var dropdown = document.getElementById("user-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == queryParams.user_id) {
           dropdown.options[i].selected = true;
       }
    }
    var dropdown = document.getElementById("author-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == queryParams.author) {
           dropdown.options[i].selected = true;
       }
    }
    var dropdown = document.getElementById("source-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == queryParams.source) {
           dropdown.options[i].selected = true;
       }
    }
    if (typeof queryParams.tags != "undefined") {
      // put a space between tags
      tags = queryParams.tags.split(",")
      document.getElementById("tags-textarea").value = tags.join(", ");
    }
    console.log("Set rating dropdown selected to " + queryParams.rating);
    var dropdown = document.getElementById("rating-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       if (dropdown.options[i].value == queryParams.rating) {
           dropdown.options[i].selected = true;
       }
    }
    var dropdown = document.getElementById("count-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       console.log(dropdown.options[i].value + "==" + queryParams.count)
       if (dropdown.options[i].value == queryParams.count) {
           console.log("set")
           dropdown.options[i].selected = true;
       }
    }
  }

  var signOutBtn =$('#sign-out');
  signOutBtn.click(function(event) {
    event.preventDefault();

    firebase.auth().signOut().then(function() {
      console.log("Sign out successful");
      userIdToken = null;
    }, function(error) {
      console.log(error);
    });
  });

  configureFirebaseLogin();
});

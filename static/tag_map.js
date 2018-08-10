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
      console.log("onAuthStateChanged entered");
      parseQueryParams(window.location.search.substr(1));
      fillForm();

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
    console.log("qstr:" + qstr);
    var arr = qstr.split("&");
    for (var i = 0; i < arr.length; i++) {
        console.log("arr: " + arr[i]);
        if (/=/.test(arr[i])) {
            var p = arr[i].split("=");
            var val = decodeURIComponent(p[1].replace(/\+/g, ' '));
            console.log(p[0] + " = " + val);
            queryParams[p[0]] = val;
        }
    }
  }

  function fillForm() {
    console.log("Set sort-by dropdown selected to " + queryParams.sort_by);
    var dropdown = document.getElementById("sort-by-dropdown");
    dropdown.options[0].selected = true;
    for (var i = 0; i < dropdown.options.length; i++) {
       console.log(dropdown.options[i].value + "==" + queryParams.sort_by)
       if (dropdown.options[i].value == queryParams.sort_by) {
           console.log("set")
           dropdown.options[i].selected = true;
       }
    }
  }

  var sortByDrop = $('#sort-by-dropdown');
  sortByDrop.change(function(event) {
    event.preventDefault();
    url = backendHostUrl + '/tagmap?sort_by=' + sortByDrop.val();
    console.log("sortByDrop: redirect to " + url);
    window.location.href=url;
  });

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

var app = angular.module('pm', ['ui.router']).config(function($rootScopeProvider){
	$rootScopeProvider.digestTtl(20); // for the tree recursion
});

app.config(['$stateProvider', '$locationProvider', '$urlRouterProvider', '$urlMatcherFactoryProvider',
	function($stateProvider, $locationProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $urlMatcherFactoryProvider.type("nonURIEncoded", {
        encode: function(val) { return val != null ? val.toString() : val; },
        decode: function(val) { return val != null ? val.toString() : val; },
        is: function(val) { return true; }
    });

		$stateProvider
			.state('photos', {
				abstract: true,
				url: "/photos",
				template: "<ui-view />"
			})
			.state('photos.list', {
				url: '?{offset:int}&{limit:int}&date&aperture&exposure&focal_length&focal_length_35&iso&make&model&lens&dirname&sort&{dnv:int}&{group:bool}&{mv:int}&{lv:int}&{dv:int}',
				templateUrl: '/static/partials/photos/photos.html',
				controller: 'PhotosOverviewCtrl',
				params: {
					offset: {dynamic: true, value: null}, 
					limit: {dynamic: true, value: null},
					group: {dynamic: true, value: false}, // dirname view state
					aperture: {dynamic: true, value: null},
					exposure: {dynamic: true, value: null},
					focal_length: {dynamic: true, value: null},
					focal_length_35: {dynamic: true, value: null},
					sort: {dynamic: true, value: null}, 
					iso: {dynamic: true, value: null},
					make: {dynamic: true, value: null},
					model: {dynamic: true, value: null, replace: [{from: '', to: ''}]},
					mv: {dynamic: true, value: 0}, // model view state
					lens: {dynamic: true, value: null, replace: [{from: '', to: ''}]},
					lv: {dynamic: true, value: 0}, // lens view state
					dirname: {dynamic: true, value: "/", replace: [{from: '', to: '/'}]},
					dnv: {dynamic: true, value: 0}, // dirname view state
					date: {dynamic: true, value: null, replace: [{from: '', to: ''}]},
					dv: {dynamic: true, value: 0}, // date view state
				}
			})
			.state('photos.details', {
				url: '/{id:int}',
				templateUrl: '/static/partials/photos/single.html',
				controller: 'PhotoCtrl',
				params: {
					id: {dynamic: true, value: 0}
				}
			});

		$urlRouterProvider.otherwise('/photos');

		$locationProvider.html5Mode(true);
	}]);


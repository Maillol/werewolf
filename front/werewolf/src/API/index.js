import autobahn from 'autobahn'
import when from 'when'


var onSubscribeWithSuccess = function (sub) {
    console.log('subscribed to topic', sub.topic);
};

var onSubscribeWithError = function (error) {
    console.log('failed to subscribe to topic', error);
};

var subscribeAfterJoinGameFactory = function (gameName, playerName) {
    return function (result) {
        var prefix = `com.werewolf.${gameName}`;
        that.session.subscribe(`${prefix}.enter_in_phase`,
                               that.$onEnterInPhase.bind(that),
                               {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);
        that.session.subscribe(`${prefix}.select_player`,
                               that.$onSelectedPlayer.bind(that)).then(onSubscribeWithSuccess, onSubscribeWithError);
        that.session.subscribe(`${prefix}.close_phase`,
                               that.$onClosePhase.bind(that),
                               {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);
        that.session.subscribe(`${prefix}.add_player`,
                                that.$onPlayerJoin.bind(that)).then(onSubscribeWithSuccess, onSubscribeWithError);
        that.session.subscribe(`${prefix}.user.${playerName}.start_game`,
                                that.$onPlayerStartGame.bind(that)).then(onSubscribeWithSuccess, onSubscribeWithError);
        return result;
    }
}

/* callbacks:
    - onSelectedPlayer(Player)
    - onEnterInPhase({phase: str, is_night: bool})
    - onRoleAffected(role: str)
    - onPlayerSelectable(selectable: List[Player], active: List[Player])
    - onPlayerJoin(currentPlayers: List[Player])
    - onClosePhase({killed: List[Player], resurrected: List[Player], winner: str})
*/
export default class API {
    constructor(url, realm) {
        this.url = url;
        this.realm = realm;
    }
    connect() {
        var connection = new autobahn.Connection(
            {url: this.url, realm: this.realm});

        var promise = when.promise(function(resolve) {
            connection.onopen = function (session) {
                console.log('Connected to crossbar');
                resolve(session);
            };
            connection.open();
        });

        var api = this;
        return promise.then(
            function(session) {
                api.session = session;

                var onAnyEvent = function(args, kwargs, details) {
                    console.log('Event received on', details.topic, args, kwargs);
                };
                session.subscribe('com.werewolf', onAnyEvent, {match: 'prefix'}).then(
                   function (sub) {
                      console.log('subscribed to topic', sub.topic);
                   },
                   function (error) {
                      console.log('failed to subscribe to topic', error);
                   }
                );

                return api;
            },
            function(error) {
                console.log('failed to open session', error);
                throw error;
            }
        );
    }
    createGame(gameName, playerName) {
        var that=this;
        return this.session.call('com.werewolf.create_game', [gameName, playerName]).then(
            subscribeAfterJoinGameFactory(gameName, playerName),
            function (error) {
                throw error;
            }
        );
    }
    joinGame(gameName, playerName) {
        var that=this;
        return this.session.call('com.werewolf.join_game', [gameName, playerName]).then(
            subscribeAfterJoinGameFactory(gameName, playerName),
            function (error) {
                throw error;
            }
        );
    }
    startGame(gameName) {
        return this.session.call('com.werewolf.start_game', [gameName]);
    }
    selectPlayer(gameName, selectPlayer, playerName) {
        return this.session.call('com.werewolf.select_player', [gameName, selectPlayer, playerName]).then(
            function (result) {
                if (result) {
                    console.log('player selected !');
                } else {
                    console.log('player not selected !');
                }
                return result;
            },
            function (error) {
                throw error;
            }
        );
    }
    $onPlayerStartGame(args, kwargs, details) {
        console.log(kwargs);  // TODO remove it.
        var role = args[0].role;
        var field = details.topic.split('.');
        var gameName = field[2];
        var playerName = field[4];
        var prefix = `com.werewolf.${gameName}.role.${role}`;

        this.session.subscribe(`${prefix}.enter_in_phase`,
            this.$onEnterInPhase, {match: "prefix"}).then(onSubscribeWithSuccess, onSubscribeWithError);
        this.session.subscribe(`${prefix}.select_player`,
            this.$onSelectedPlayer).then(onSubscribeWithSuccess, onSubscribeWithError);

        var that = this;
        return this.session.call('com.werewolf.player_listen_topic', [gameName, playerName]).then(
            function (result) {
                console.log('RPC com.werewolf.player_listen_topic OK');
                if (that.onRoleAffected !== undefined) {
                    that.onRoleAffected(role);
                }
                return result;
            },
            function (error) {
                throw error;
            }
        );
    }
    $onEnterInPhase(args, kwargs, details) {
        var phase = details.topic.substring(details.topic.lastIndexOf('.') + 1);
        if (args[0].is_night !== undefined && this.onEnterInPhase !== undefined) {
            this.onEnterInPhase({phase: phase, is_night: args[0].is_night});
        }
        if (args[0].selectable !== undefined && this.onPlayerSelectable !== undefined) {
            this.onPlayerSelectable(args[0].selectable, args[0].active);
        }
    }
    $onSelectedPlayer(args, kwargs, details) {
        console.log(args, kwargs, details);
        if (this.onSelectedPlayer !== undefined) {
            this.onSelectedPlayer(args[0]);
        }
    }
    $onPlayerJoin(args, kwargs, details) {
        console.log(args, kwargs, details);
        if (this.onPlayerJoin !== undefined) {
            this.onPlayerJoin(args[0]);
        }
    }
    $onClosePhase(args, kwargs, details) {
        console.log(args, kwargs, details);
        args[0]['phase'] = details.topic.substring(details.topic.lastIndexOf('.') + 1);
        if (this.onClosePhase !== undefined) {
            this.onClosePhase(args[0]);
        }
    }
}

from dishka import Provider, Scope, provide

from application import interactors


class AppProvider(Provider):

    create_bot_interactor = provide(interactors.CreateBot, scope=Scope.REQUEST)
    create_bots_interactor = provide(interactors.CreateBots, scope=Scope.REQUEST)
    delete_bot_interactor = provide(interactors.DeleteBot, scope=Scope.REQUEST)
    get_bot_interactor = provide(interactors.GetBot, scope=Scope.REQUEST)
    get_bots_interactor = provide(interactors.GetBots, scope=Scope.REQUEST)
    get_bots_with_count_interactor = provide(interactors.GetBotsWithCount, scope=Scope.REQUEST)
    update_bot_interactor = provide(interactors.UpdateBot, scope=Scope.REQUEST)

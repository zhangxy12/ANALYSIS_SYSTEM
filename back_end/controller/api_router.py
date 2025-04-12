
from fastapi import APIRouter
from . import(
    tag_test_controller,
    tag_controller,
    tag_retweet_controller,
    tag_comment_controller,
    user,
    rumor,
    main_screen
)

api_router = APIRouter()

api_router.include_router(tag_test_controller.test_router, prefix='/test')
api_router.include_router(tag_controller.tag_router, prefix='/tag')
api_router.include_router(tag_retweet_controller.retweet, prefix='/tag/retweet')
api_router.include_router(tag_comment_controller.comment_router, prefix='/tag/comment')
api_router.include_router(user.user_router, prefix='/tag/user')
api_router.include_router(rumor.rumor_router, prefix='/tag/rumor')
api_router.include_router(main_screen.main_router, prefix='/tag/main')
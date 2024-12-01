from rest_framework import serializers
from signup.serializers import CustomUserSerializer
from .models import *

# 게시물
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']
        

class MainBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_scraped = serializers.SerializerMethodField(read_only=True)
    writer = CustomUserSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = MainBoard
        fields = ['id', 'board_title', 'title', 'body', 'writer', 'anonymous', 'time', 
                  'comments_count', 'likes_count', 'scraps_count', 'is_liked', 'is_scraped', 'images']

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.like.filter(id=user.id).exists()

    def get_is_scraped(self, obj):
        user = self.context['request'].user
        return obj.scrap.filter(id=user.id).exists()



class SchoolBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_scraped = serializers.SerializerMethodField(read_only=True)
    board_title = serializers.CharField(read_only=True)  
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolBoard
        fields = ['id', 'board_title', 'title', 'body', 'writer', 'anonymous', 
                  'school_name', 'time', 'comments_count', 'likes_count', 'scraps_count', 
                  'is_liked', 'is_scraped']

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.like.filter(id=user.id).exists()

    def get_is_scraped(self, obj):
        user = self.context['request'].user
        return obj.scrap.filter(id=user.id).exists()


class QuestionBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_scraped = serializers.SerializerMethodField(read_only=True)
    board_title = serializers.SerializerMethodField() 
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = QuestionBoard
        fields = ['id', 'track', 'board_title', 'title', 'body', 'writer', 'anonymous', 
                  'school_name', 'time', 'comments_count', 'likes_count', 'scraps_count', 
                  'is_liked', 'is_scraped']

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_board_title(self, obj):
        return dict(QuestionBoard.BOARD_CHOICES).get(obj.track)  

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.like.filter(id=user.id).exists()

    def get_is_scraped(self, obj):
        user = self.context['request'].user
        return obj.scrap.filter(id=user.id).exists()
    
    
class MainNoticeBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_scraped = serializers.SerializerMethodField(read_only=True)
    board_title = serializers.CharField(read_only=True)  
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = MainNoticeBoard
        fields = ['id', 'board_title', 'title', 'body', 'writer', 'anonymous', 
                  'time', 'comments_count', 'likes_count', 'scraps_count', 'is_liked', 'is_scraped']

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.like.filter(id=user.id).exists()

    def get_is_scraped(self, obj):
        user = self.context['request'].user
        return obj.scrap.filter(id=user.id).exists()
    
    
class SchoolNoticeBoardSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    scraps_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    is_scraped = serializers.SerializerMethodField(read_only=True)
    board_title = serializers.CharField(read_only=True)  
    writer = CustomUserSerializer(read_only=True)

    class Meta:
        model = SchoolNoticeBoard
        fields = ['id', 'board_title', 'title', 'body', 'writer', 'anonymous', 
                  'school_name', 'time', 'comments_count', 'likes_count', 'scraps_count', 
                  'is_liked', 'is_scraped']

    def get_comments_count(self, obj):
        return obj.comments_count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.like.filter(id=user.id).exists()

    def get_is_scraped(self, obj):
        user = self.context['request'].user
        return obj.scrap.filter(id=user.id).exists()


# 댓글
class BaseCommentSerializer(serializers.ModelSerializer):
    anonymous_number = serializers.IntegerField(read_only=True)  # 익명 번호
    is_author = serializers.SerializerMethodField()  # 작성자인지 여부
    writer = CustomUserSerializer(read_only=True)
    board_title = serializers.SerializerMethodField()  
    post_info = serializers.SerializerMethodField()

    class Meta:
        model = None  
        fields = ['id', 'content', 'writer', 'anonymous', 'anonymous_number', 'is_author', 
                  'time', 'board', 'board_title', 'post_info'] 

    def get_is_author(self, obj):
        return obj.writer == obj.board.writer  # 댓글 작성자가 게시물 작성자인지 확인

    def get_writer(self, obj):
        if obj.anonymous:
            return {"nickname": f"익명 {obj.anonymous_number}"}
        return {"nickname": obj.writer.nickname}
    
    def get_board_title(self, obj):
        if isinstance(obj.board, QuestionBoard):
            return dict(QuestionBoard.BOARD_CHOICES).get(obj.board.track)
        return getattr(obj.board, 'board_title', None) 

    def get_post_info(self, obj):
        board = obj.board
        post_data = {
            "title": board.title,  # 게시글 제목
            "body": board.body,  # 게시글 내용
            "images": PostImageSerializer(board.images.all(), many=True).data,  # 게시글 이미지
            "comments_count": board.comments_count()  # 게시글 댓글 수
        }
        return post_data


class MainCommentSerializer(BaseCommentSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=MainBoard.objects.all())  # MainBoard와 연결

    class Meta(BaseCommentSerializer.Meta):
        model = MainComment
        fields = BaseCommentSerializer.Meta.fields


class SchoolCommentSerializer(BaseCommentSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=SchoolBoard.objects.all())  # SchoolBoard와 연결
    school_name = serializers.SerializerMethodField()  

    class Meta(BaseCommentSerializer.Meta):
        model = SchoolComment
        fields = BaseCommentSerializer.Meta.fields + ['school_name'] 

    def get_school_name(self, obj):
        return obj.board.school_name  



class QuestionCommentSerializer(BaseCommentSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=QuestionBoard.objects.all())  # QuestionBoard와 연결
    school_name = serializers.SerializerMethodField() 

    class Meta(BaseCommentSerializer.Meta):
        model = QuestionComment
        fields = BaseCommentSerializer.Meta.fields + ['school_name']

    def get_school_name(self, obj):
        return obj.board.school_name  


class MainNoticeCommentSerializer(BaseCommentSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=MainNoticeBoard.objects.all())  # MainNoticeBoard와 연결

    class Meta(BaseCommentSerializer.Meta):
        model = MainNoticeComment
        fields = BaseCommentSerializer.Meta.fields


class SchoolNoticeCommentSerializer(BaseCommentSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=SchoolNoticeBoard.objects.all())  # SchoolNoticeBoard와 연결
    school_name = serializers.SerializerMethodField() 

    class Meta(BaseCommentSerializer.Meta):
        model = SchoolNoticeComment
        fields = BaseCommentSerializer.Meta.fields + ['school_name']

    def get_school_name(self, obj):
        return obj.board.school_name 

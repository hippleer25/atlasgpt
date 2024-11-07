import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Linking,
  Dimensions,
  Animated,
} from 'react-native';
import { useFonts } from 'expo-font';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTitleVisible, setIsTitleVisible] = useState(true);
  const [textInputHeight, setTextInputHeight] = useState(40);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isScrollbarVisible, setIsScrollbarVisible] = useState(false);
  const scrollViewRef = useRef();
  const maxTextInputHeight = Dimensions.get('window').height * 0.3;
  const buttonColorAnim = useRef(new Animated.Value(0)).current;

  const [fontsLoaded] = useFonts({
    'Yantramanav-Bold': require('./assets/fonts/Yantramanav-Bold.ttf'),
  });

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const tokenResponse = await fetch('http://143.54.117.114:5000/api/token');
        const tokenData = await tokenResponse.json();
        setToken(tokenData.user_token);
        console.log('Token:', tokenData.user_token);
      } catch (error) {
        console.error('Failed to fetch token:', error);
      }
    };

    fetchToken();
  }, []);

  useEffect(() => {
    Animated.timing(buttonColorAnim, {
      toValue: isLoading ? 1 : 0,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [isLoading]);

  const sendMessage = async (text) => {
    if (text.trim() === '' || isLoading) return;

    const userMessage = { type: 'user', text: text };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputText('');
    setTextInputHeight(40);
    setIsScrollbarVisible(false);
    setIsTitleVisible(false);
    setIsLoading(true);

    if (!token) {
      console.error('No token available');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://143.54.117.114:5000/api?q=${encodeURIComponent(text)}&t=${encodeURIComponent(token)}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let textChunk = '';

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value, { stream: !done });
        textChunk += chunk;

        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          if (updatedMessages[updatedMessages.length - 1].type === 'bot') {
            updatedMessages[updatedMessages.length - 1] = { ...updatedMessages[updatedMessages.length - 1], text: textChunk };
          } else {
            updatedMessages.push({ type: 'bot', text: textChunk });
          }
          return updatedMessages;
        });

        if (textChunk.trim() !== '') {
          setIsLoading(false);
        }

        await new Promise((resolve) => setTimeout(resolve, 1));
      }
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { type: 'bot', text: `Erro: ${error.message}` },
      ]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.nativeEvent.key === 'Enter' && !e.nativeEvent.shiftKey) {
      e.preventDefault();
      sendMessage(inputText);
    }
  };

  const handleButtonPress = (text) => {
    setInputText(text);
    sendMessage(text);
  };

  const handleContentSizeChange = (event) => {
    const newHeight = event.nativeEvent.contentSize.height;
    setTextInputHeight(newHeight);
    setIsScrollbarVisible(newHeight >= maxTextInputHeight);
  };

  const { width } = Dimensions.get('window');
  const isDesktop = width >= 1024;

  const formatText = (text) => {
    const paragraphs = text.split('\n\n');

    return paragraphs.map((paragraph, paragraphIndex) => {
      const lines = paragraph.split('\n');

      const formattedLines = lines.map((line, lineIndex) => {
        const parts = line.split(/(\*\*[^*]+\*\*|_[^_]+_)/g);

        const formattedParts = parts.map((part, partIndex) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <Text key={`${paragraphIndex}-${lineIndex}-${partIndex}`} style={styles.bold}>
                {part.slice(2, -2)}
              </Text>
            );
          } else if (part.startsWith('_') && part.endsWith('_')) {
            return (
              <Text key={`${paragraphIndex}-${lineIndex}-${partIndex}`} style={styles.italic}>
                {part.slice(1, -1)}
              </Text>
            );
          } else {
            return <Text key={`${paragraphIndex}-${lineIndex}-${partIndex}`}>{part}</Text>;
          }
        });

        return (
          <Text key={`${paragraphIndex}-${lineIndex}`} style={lineIndex !== 0 ? { marginTop: 5 } : {}}>
            {formattedParts}
          </Text>
        );
      });

      return (
        <View key={paragraphIndex} style={paragraphIndex !== 0 ? { marginTop: 15 } : {}}>
          {formattedLines}
        </View>
      );
    });
  };

  const buttonBackgroundColor = buttonColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['#0A74A6', '#808080']
  });

  if (!fontsLoaded) {
    return <View><Text>Loading...</Text></View>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.topButton}
          onPress={() => Linking.openURL('http://atlas-oportunidades.nuvem.ufrgs.br/')}
        >
          <Text style={styles.topButtonText}>IR PARA O ATLAS</Text>
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView
        style={[styles.contentContainer, isDesktop && styles.desktopContainer]}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContainer}
          ref={scrollViewRef}
          onContentSizeChange={() => scrollViewRef.current.scrollToEnd({ animated: true })}
        >
          {isTitleVisible && (
            <View style={styles.titleContainer}>
              <View style={styles.titleContent}>
                <Text style={styles.title}>AtlasGPT</Text>
                <Text style={styles.titleDescription}>
                  Com o AtlasGPT, você receberá recomendações precisas para abertura de negócios, aprimorado com inteligência artificial. Conte um pouco mais sobre você e sobre os projetos que gostaria de iniciar. O AtlasGPT o guiará pelo mundo dos negócios!
                </Text>
              </View>
            </View>
          )}

          {messages.map((msg, index) => (
            <View key={index} style={[styles.messageContainer, msg.type === 'user' ? styles.userMessage : styles.botMessage]}>
              <Text style={[styles.messageText, msg.type === 'bot' && styles.botMessageText]}>
                {formatText(msg.text)}
              </Text>
            </View>
          ))}

          {isLoading && (
            <View style={[styles.messageContainer, styles.botMessage]}>
              <Text style={[styles.messageText, styles.botMessageText]}>...</Text>
            </View>
          )}
        </ScrollView>

        {isTitleVisible && (
          <View style={styles.buttonContainer}>
            <View style={styles.infoButtons}>
              <TouchableOpacity style={styles.infoButton} onPress={() => handleButtonPress('AtlasGPT, já tenho uma ideia de onde ficaria meu nogócio!')}>
                <Text style={styles.infoButtonText}>Eu já tenho uma localização</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.infoButton} onPress={() => handleButtonPress('Eu já tenho um setor')}>
                <Text style={styles.infoButtonText}>Eu já tenho um setor</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.infoButtons}>
              <TouchableOpacity style={styles.infoButton} onPress={() => handleButtonPress('Eu tenho um setor e uma localização')}>
                <Text style={styles.infoButtonText}>Eu tenho um setor e uma localização</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.infoButton} onPress={() => handleButtonPress('Ainda não sei o local nem o setor')}>
                <Text style={styles.infoButtonText}>Ainda não sei o local nem o setor</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={[
              styles.textInput,
              {
                height: Math.min(Math.max(40, textInputHeight), maxTextInputHeight),
                scrollbarWidth: isScrollbarVisible ? 'auto' : 'none',
              },
            ]}
            multiline
            value={inputText}
            onChangeText={(text) => setInputText(text)}
            onContentSizeChange={handleContentSizeChange}
            onKeyPress={handleKeyPress}
            placeholder="Digite uma mensagem..."
            editable={!isLoading}
          />
          <Animated.View style={[styles.sendButton, { backgroundColor: buttonBackgroundColor }]}>
            <TouchableOpacity onPress={() => sendMessage(inputText)} disabled={isLoading}>
              <Text style={styles.sendButtonText}>Enviar</Text>
            </TouchableOpacity>
          </Animated.View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
    zIndex: 1000,
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  topButton: {
    backgroundColor: '#0A74A6',
    padding: 10,
    paddingHorizontal: 33,
    borderRadius: 7,
  },
  topButtonText: {
    color: '#fff',
    fontSize: 12,
    textAlign: 'center',
  },
  contentContainer: {
    flex: 1,
    marginTop: 50,
    paddingHorizontal: 10,
  },
  desktopContainer: {
    maxWidth: 1200,
    width: '50%',
    maxWidth: '43.5%',
    alignSelf: 'center',
    padding: 20,
    height: '100%',
    marginHorizontal: 'auto',
  },
  scrollContainer: {
    padding: 15,
    flexGrow: 1,
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  titleContent: {
    alignItems: 'center',
  },
  title: {
    marginTop: 45,
    fontSize: 136,
    fontFamily: 'Yantramanav-Bold',
    color: '#0A74A6',
  },
  titleDescription: {
    marginTop: 0,
    marginBottom: 20,
    fontSize: 19,
    color: '#616161',
    textAlign: 'center',
  },
  buttonContainer: {
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%',
    marginBottom: 10,
    gap: 10,
  },
  infoButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    width: '100%',
    gap: 10,
    marginBottom: 0,
  },
  infoButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 15,
    borderRadius: 7,
    borderWidth: 1,
    borderColor: '#0A74A6',
    justifyContent: 'center',
    alignItems: 'center',
    flex: 1,
    maxWidth: '50%',
  },
  infoButtonText: {
    color: '#212121',
    fontSize: 19,
  },
  inputContainer: {
    borderTopWidth: 1,
    borderTopColor: '#ddd',
    padding: 10,
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#fff',
  },
  textInput: {
    flex: 1,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 7,
    padding: 10,
    backgroundColor: '#f4f4f4',
    fontSize: 19,
    maxHeight: Dimensions.get('window').height * 0.3,
  },
  sendButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 7,
    marginLeft: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 19,
  },
  messageContainer: {
    maxWidth: '80%',
    padding: 10,
    borderRadius: 7,
    marginBottom: 10,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#0A74A6',
  },
  botMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f1f1f1',
  },
  messageText: {
    color: '#fff',
    fontSize: 19,
  },
  botMessageText: {
    color: '#000',
    fontSize: 19,
  },
  bold: {
    fontWeight: 'bold',
  },
  italic: {
    fontStyle: 'italic',
  },
});

export default App;

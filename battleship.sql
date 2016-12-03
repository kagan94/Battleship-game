/*
Navicat MySQL Data Transfer

Source Server         : 1
Source Server Version : 50626
Source Host           : 127.0.0.1:3306
Source Database       : battleship

Target Server Type    : MYSQL
Target Server Version : 50626
File Encoding         : 65001

Date: 2016-12-03 16:49:28
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for invitations
-- ----------------------------
DROP TABLE IF EXISTS `invitations`;
CREATE TABLE `invitations` (
  `invitation_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `initiator_id` int(11) DEFAULT NULL COMMENT 'Player whi inizialized the invitation',
  `invited_player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`invitation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of invitations
-- ----------------------------

-- ----------------------------
-- Table structure for maps
-- ----------------------------
DROP TABLE IF EXISTS `maps`;
CREATE TABLE `maps` (
  `map_id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`map_id`),
  KEY `player_id` (`owner_id`),
  CONSTRAINT `maps_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `players` (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of maps
-- ----------------------------

-- ----------------------------
-- Table structure for players
-- ----------------------------
DROP TABLE IF EXISTS `players`;
CREATE TABLE `players` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of players
-- ----------------------------

-- ----------------------------
-- Table structure for players_hits
-- ----------------------------
DROP TABLE IF EXISTS `players_hits`;
CREATE TABLE `players_hits` (
  `shot_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `player_id` int(11) DEFAULT NULL,
  `raw` int(5) DEFAULT NULL,
  `column` int(5) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `hit` int(1) DEFAULT NULL COMMENT 'If shot hit in someone = 1, otherwise 0',
  PRIMARY KEY (`shot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of players_hits
-- ----------------------------

-- ----------------------------
-- Table structure for player_to_map
-- ----------------------------
DROP TABLE IF EXISTS `player_to_map`;
CREATE TABLE `player_to_map` (
  `map_id` int(11) NOT NULL,
  `player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`map_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_to_map
-- ----------------------------

-- ----------------------------
-- Table structure for ship_placement
-- ----------------------------
DROP TABLE IF EXISTS `ship_placement`;
CREATE TABLE `ship_placement` (
  `map_id` int(11) NOT NULL,
  `player_id` int(11) DEFAULT NULL,
  `raw_start` int(5) DEFAULT NULL,
  `raw_end` int(5) DEFAULT NULL,
  `column_start` int(5) DEFAULT NULL,
  `column_end` int(5) DEFAULT NULL,
  `ship_type` set('1','2','3','4') DEFAULT '1' COMMENT 'size of ship',
  PRIMARY KEY (`map_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of ship_placement
-- ----------------------------
